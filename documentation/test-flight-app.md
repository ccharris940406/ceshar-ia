# TestFlightApp

A real-time flight tracker mobile app built with React Native and Expo. It detects your current location and shows nearby aircraft on an interactive map, pulling live flight data from the AirLabs API.

## Features

- **Live flight map** — displays nearby aircraft as directional icons on an interactive map, rotated according to their heading
- **Radius filter** — adjust the search radius (5–1000 km) with a slider to control how many flights appear
- **Flight list** — scrollable list of all flights within the selected radius
- **Location-aware** — automatically centers on the user's GPS position on launch
- **Dark/light theme** — adapts to the device's system appearance

## Stack

| Layer | Technology |
|---|---|
| Framework | [Expo](https://expo.dev) ~54 / React Native 0.79 |
| Routing | Expo Router |
| Maps | react-native-maps |
| Location | expo-location |
| Flight data | [AirLabs API](https://airlabs.co) v9 |
| Language | TypeScript |

## Getting started

### 1. Prerequisites

- Node.js 18+
- [pnpm](https://pnpm.io) (or npm)
- Expo Go app on your device, or an Android/iOS simulator
- A free AirLabs API key from [airlabs.co](https://airlabs.co)

### 2. Clone and install

```bash
git clone <repo-url>
cd TestFlightApp
pnpm install
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
API_URL=https://airlabs.co/api/v9
AIRLABS_API_KEY=your_api_key_here
```

### 4. Run the app

```bash
# Start the Expo dev server
npx expo start

# Run on a specific platform
npx expo start --android
npx expo start --ios
npx expo start --web
```

Scan the QR code with the Expo Go app or press `a` / `i` to open a simulator.

## Project structure

```
app/
  index.tsx          # Main screen — map + filter + flight list
  _layout.tsx        # Root layout
components/
  TFAMap.tsx         # Interactive map with flight markers
  TFAFilter.tsx      # Radius slider
  TFAFlightsList.tsx # Scrollable list of flights
hooks/
  useNearlyFlights.ts  # Fetches flights from AirLabs within a bounding box
  useUserLocation.ts   # Retrieves the device's GPS coordinates
```

## How it works

1. On launch, `useUserLocation` requests GPS permission and returns the device coordinates.
2. `useNearlyFlights` converts the selected radius into a bounding box and queries the AirLabs `/flights` endpoint.
3. `TFAMap` renders each flight as a rotated airplane icon (`MaterialCommunityIcons`) at its reported position.
4. The radius slider triggers a new API call, updating both the map and the list.
