import { View, Text, ScrollView, StyleSheet, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useState } from 'react';
import { API_ENDPOINTS } from '../../config/api';

export default function ScanResultScreen() {
  const params = useLocalSearchParams();
  const router = useRouter();
  const [loadingIngredients, setLoadingIngredients] = useState<Set<string>>(new Set());
  const [progressMessages, setProgressMessages] = useState<Record<string, string>>({});
  
  let scanData: { product: any; flagged_ingredients: string[] } = { product: {}, flagged_ingredients: [] };
  try {
    const raw = Array.isArray(params.scanData) ? params.scanData[0] : params.scanData;
    if (raw) {
      scanData = JSON.parse(raw);
      console.log(scanData)
    }
  } catch (err) {
    console.error("Failed to parse scan data param:", err);
  }

  const handleIngredientPress = async (ingredient: string) => {
    if (loadingIngredients.has(ingredient)) return;
    
    setLoadingIngredients(prev => new Set(prev).add(ingredient));
    
    try {
      const response = await fetch(API_ENDPOINTS.INGREDIENT_BRIEF, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ ingredient }),
      });

      if (!response.ok) {
        throw new Error("Failed to get ingredient brief");
      }

      const briefData = await response.json();
      console.log("Brief data received:", briefData);

      if (briefData.in_progress) {
        // Start polling for progress
        pollForProgress(ingredient);
      } else {
        // Brief is ready, navigate immediately
        router.push(`/ingredientbrief?ingredient=${encodeURIComponent(briefData.ingredient)}&summary=${encodeURIComponent(briefData.summary)}` as any);
        setLoadingIngredients(prev => {
          const newSet = new Set(prev);
          newSet.delete(ingredient);
          return newSet;
        });
      }

    } catch (err) {
      console.error("Brief error:", err);
      Alert.alert(
        "Error",
        `Could not retrieve brief for ${ingredient}: ${err instanceof Error ? err.message : String(err)}`
      );
      setLoadingIngredients(prev => {
        const newSet = new Set(prev);
        newSet.delete(ingredient);
        return newSet;
      });
    }
  };

  const pollForProgress = async (ingredient: string) => {
    const pollInterval = 2000; // Poll every 2 seconds
    const maxAttempts = 60; // Max 2 minutes
    let attempts = 0;

    const poll = async () => {
      try {
        const response = await fetch(`${API_ENDPOINTS.INGREDIENT_BRIEF_PROGRESS}/${encodeURIComponent(ingredient)}`);
        if (!response.ok) {
          throw new Error("Failed to get progress");
        }

        const progress = await response.json();
        console.log("Progress update:", progress);

        // Update progress message
        setProgressMessages(prev => ({
          ...prev,
          [ingredient]: progress.message || "Processing..."
        }));

        if (progress.status === "completed") {
          // Generation complete, navigate to brief
          router.push(`/ingredientbrief?ingredient=${encodeURIComponent(ingredient)}&summary=${encodeURIComponent(progress.summary)}` as any);
          setLoadingIngredients(prev => {
            const newSet = new Set(prev);
            newSet.delete(ingredient);
            return newSet;
          });
          setProgressMessages(prev => {
            const newMessages = { ...prev };
            delete newMessages[ingredient];
            return newMessages;
          });
        } else if (progress.status === "failed") {
          // Generation failed
          Alert.alert("Error", progress.message || "Failed to generate brief");
          setLoadingIngredients(prev => {
            const newSet = new Set(prev);
            newSet.delete(ingredient);
            return newSet;
          });
          setProgressMessages(prev => {
            const newMessages = { ...prev };
            delete newMessages[ingredient];
            return newMessages;
          });
        } else if (attempts < maxAttempts) {
          // Still in progress, continue polling
          attempts++;
          setTimeout(poll, pollInterval);
        } else {
          // Timeout
          Alert.alert("Timeout", "Brief generation is taking longer than expected. Please try again.");
          setLoadingIngredients(prev => {
            const newSet = new Set(prev);
            newSet.delete(ingredient);
            return newSet;
          });
          setProgressMessages(prev => {
            const newMessages = { ...prev };
            delete newMessages[ingredient];
            return newMessages;
          });
        }
      } catch (err) {
        console.error("Progress polling error:", err);
        Alert.alert("Error", "Failed to check progress");
        setLoadingIngredients(prev => {
          const newSet = new Set(prev);
          newSet.delete(ingredient);
          return newSet;
        });
        setProgressMessages(prev => {
          const newMessages = { ...prev };
          delete newMessages[ingredient];
          return newMessages;
        });
      }
    };

    // Start polling
    setTimeout(poll, pollInterval);
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Scan Results</Text>
      <Text style={styles.subtitle}>{scanData.product.name || 'Product'}</Text>
      <Text style={styles.summary}>
        {scanData.flagged_ingredients.length > 0 
          ? `Found ${scanData.flagged_ingredients.length} flagged ingredient(s). Tap to view research briefs.`
          : "No flagged ingredients found in this product."
        }
      </Text>
      
      {scanData.flagged_ingredients.map((ingredient, idx) => (
        <TouchableOpacity 
          key={idx} 
          style={styles.ingredientButton}
          onPress={() => handleIngredientPress(ingredient)}
          disabled={loadingIngredients.has(ingredient)}
        >
          <View style={styles.ingredientContent}>
            <View style={styles.ingredientTextContainer}>
              <Text style={styles.ingredientText}>{ingredient}</Text>
              {loadingIngredients.has(ingredient) && progressMessages[ingredient] && (
                <Text style={styles.progressText}>{progressMessages[ingredient]}</Text>
              )}
            </View>
            {loadingIngredients.has(ingredient) ? (
              <ActivityIndicator size="small" color="#fff" />
            ) : (
              <Text style={styles.buttonText}>View Brief →</Text>
            )}
        </View>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, backgroundColor: '#000' },
  title: { fontSize: 56, fontWeight: 'bold', marginBottom: 8, marginTop: 64, color: 'white' },
  subtitle: { fontSize: 24, fontWeight: '600', marginBottom: 16, color: '#ccc' },
  summary: { fontSize: 18, color: 'white', marginBottom: 24, lineHeight: 24 },
  ingredientButton: {
    backgroundColor: '#333',
    borderRadius: 12,
    marginBottom: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#555',
  },
  ingredientContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  ingredientTextContainer: {
    flex: 1,
  },
  ingredientText: {
    fontSize: 18,
    fontWeight: '600',
    color: 'white',
  },
  progressText: {
    fontSize: 14,
    color: '#ccc',
    marginTop: 4,
    fontStyle: 'italic',
  },
  buttonText: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '500',
  },
});
