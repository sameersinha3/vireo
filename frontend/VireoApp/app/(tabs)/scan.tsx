import { CameraView, CameraType, useCameraPermissions } from 'expo-camera';
import { useState } from 'react';
import { Button, StyleSheet, Text, TouchableOpacity, View, ActivityIndicator, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { API_ENDPOINTS } from '../../config/api';


export default function TabTwoScreen() {
  const [facing, setFacing] = useState<CameraType>('back');
  const [permission, requestPermission] = useCameraPermissions();
  const [scanned, setScanned] = useState(false); // Tracks if a barcode has been processed recently
  const [loading, setLoading] = useState(false); // Indicates if an API call is in progress
  const router = useRouter();

  if (!permission) return <View />;
  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>We need your permission to show the camera</Text>
        <Button onPress={requestPermission} title="Grant Permission" />
      </View>
    );
  }

  function toggleCameraFacing() {
    // Only allow camera flip if not currently loading
    if (!loading) {
      setFacing(current => (current === 'back' ? 'front' : 'back'));
    }
  }

  const handleBarcodeScanned = async ({ data }: { data: string }) => {
    if (scanned || loading) {
      return;
    }

    setScanned(true); // Mark as scanned to prevent immediate re-scanning
    setLoading(true); // Indicate that an API call is starting (show loading screen)

    try {
      console.log("Barcode scanned:", data);
      console.log("Making request to:", API_ENDPOINTS.SCAN);
      const response = await fetch(API_ENDPOINTS.SCAN, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ barcode: data }),
      });

      if (!response.ok) {
        throw new Error("Product not found or server error");
      }

      const res = await response.json();
      console.log("API Response received:", res);

      router.push({
        pathname: "/(tabs)/scanresultscreen",
        params: {
          scanData: JSON.stringify(res), // Pass the complete response
        },
      });

    } catch (err) {
      console.error("Scan error:", err);
      Alert.alert(
        "Scan Error",
        `Could not retrieve product information: ${err instanceof Error ? err.message : String(err)}. Please try again.`
      );
    } finally {
      // Always stop loading and reset scanned state, regardless of success or failure.
      // This allows the user to scan again if they return to this screen or if an error occurred.
      setLoading(false);
      setScanned(false);
    }
  };


  return (
    <View style={styles.container}>
      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#0000ff" />
          <Text style={styles.loadingText}>Conducting Research (this could take a minute)...</Text>
        </View>
      ) : (
        <CameraView
          style={styles.camera}
          facing={facing}
          barcodeScannerSettings={{
            barcodeTypes: ['qr', 'code128', 'ean13'],
          }}
          // IMPORTANT: Conditionally disable barcode scanning when loading
          // By setting onBarcodeScanned to undefined, the camera stops emitting events
          onBarcodeScanned={scanned ? undefined : handleBarcodeScanned}
        >
          <View style={styles.buttonContainer}>
            <TouchableOpacity style={styles.button} onPress={toggleCameraFacing}>
              <Text style={styles.text}>Flip Camera</Text>
            </TouchableOpacity>
          </View>
        </CameraView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center', // Center content for loading screen
  },
  message: {
    textAlign: 'center',
    paddingBottom: 10,
  },
  camera: {
    flex: 1,
    width: '100%', // Ensure camera takes full width
  },
  buttonContainer: {
    flex: 1,
    flexDirection: 'row',
    backgroundColor: 'transparent',
    margin: 64,
  },
  button: {
    flex: 1,
    alignSelf: 'flex-end',
    alignItems: 'center',
  },
  text: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 18,
    color: '#333',
    textAlign: 'center',
    paddingHorizontal: 20,
  },
});