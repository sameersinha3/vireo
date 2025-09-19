import { View, Text, ScrollView, StyleSheet, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useState } from 'react';
import { API_ENDPOINTS } from '../../config/api';

export default function ScanResultScreen() {
  const params = useLocalSearchParams();
  const router = useRouter();
  const [loadingIngredients, setLoadingIngredients] = useState<Set<string>>(new Set());
  
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

      router.push(`/ingredientbrief?ingredient=${encodeURIComponent(briefData.ingredient)}&summary=${encodeURIComponent(briefData.summary)}` as any);

    } catch (err) {
      console.error("Brief error:", err);
      Alert.alert(
        "Error",
        `Could not retrieve brief for ${ingredient}: ${err instanceof Error ? err.message : String(err)}`
      );
    } finally {
      setLoadingIngredients(prev => {
        const newSet = new Set(prev);
        newSet.delete(ingredient);
        return newSet;
      });
    }
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
            <Text style={styles.ingredientText}>{ingredient}</Text>
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
  ingredientText: {
    fontSize: 18,
    fontWeight: '600',
    color: 'white',
    flex: 1,
  },
  buttonText: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '500',
  },
});
