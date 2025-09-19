import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';

export default function IngredientBriefScreen() {
  const params = useLocalSearchParams();
  const router = useRouter();
  
  const ingredient = params.ingredient as string;
  const summary = params.summary as string;

  return (
    <ScrollView style={styles.container}>
      <TouchableOpacity 
        style={styles.backButton}
        onPress={() => router.back()}
      >
        <Text style={styles.backButtonText}>← Back</Text>
      </TouchableOpacity>
      
      <Text style={styles.title}>{ingredient}</Text>
      <Text style={styles.subtitle}>Research Brief</Text>
      
      <View style={styles.summaryContainer}>
        <Text style={styles.summary}>{summary}</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1,
    padding: 16, 
    backgroundColor: '#000' 
  },
  backButton: {
    marginTop: 64,
    marginBottom: 16,
    alignSelf: 'flex-start',
  },
  backButtonText: {
    fontSize: 18,
    color: '#007AFF',
    fontWeight: '500',
  },
  title: { 
    fontSize: 48, 
    fontWeight: 'bold', 
    marginBottom: 8, 
    color: 'white' 
  },
  subtitle: { 
    fontSize: 20, 
    fontWeight: '600', 
    marginBottom: 24, 
    color: '#ccc' 
  },
  summaryContainer: {
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 20,
    borderWidth: 1,
    borderColor: '#333',
  },
  summary: { 
    fontSize: 16, 
    color: 'white', 
    lineHeight: 24,
    textAlign: 'justify',
  },
});
