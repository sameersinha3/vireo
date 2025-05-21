import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { useLocalSearchParams } from 'expo-router';

export default function ScanResultScreen() {
  const params = useLocalSearchParams();
  
  let summaries: Record<string, string> = {};
  try {
    const raw = Array.isArray(params.summaries) ? params.summaries[0] : params.summaries;
    if (raw) {
      summaries = JSON.parse(raw);
      console.log(summaries)
    }
  } catch (err) {
    console.error("Failed to parse summaries param:", err);
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Scan Results</Text>
      <Text style={styles.summary}>View a brief of the latest studies of potentially dangerous ingredients</Text>
      {Object.entries(summaries).map(([ingredient, summary], idx) => (
        <View key={idx} style={styles.result}>
          <Text style={styles.ingredient}>{ingredient}</Text>
          <Text style={styles.summary}>{String(summary)}</Text>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  title: { fontSize: 56, fontWeight: 'bold', marginBottom: 16, marginTop: 64, color: 'white' },
  result: { marginBottom: 12, color: 'white' },
  ingredient: { fontWeight: 'bold', fontSize: 32, color: 'white' },
  summary: { fontSize: 18, color: 'white', marginBottom: 16 }
});
