# Terravia — Flight Logs

Terravia is a drone flight logging system consisting of a **Flask REST API** backed by a **PostGIS** (geospatial PostgreSQL) database, and a **Flutter** mobile app. It tracks users and roles, pilots with their licenses, the drone fleet, missions (with GPS locations and clearance codes), and per-mission flight logs with take-off/landing times.

```
flightlogs/
├── api/    Flask REST API (Docker: web + PostGIS db + pgAdmin)
└── app/    Flutter mobile app (Android)
```

## Requirements

- **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** — runs the API, the PostGIS database, and pgAdmin
- **[Flutter SDK](https://docs.flutter.dev/get-started/install/windows)** (Dart ^3.13) with the Android toolchain, installed via **[Android Studio](https://developer.android.com/studio)** (its SDK manager provides the Android SDK and platform tools)
- **An Android phone** with USB debugging enabled (Settings → About phone → tap Build number 7× to unlock Developer options, then enable USB debugging), connected to the **same Wi-Fi network** as your PC

After installing, run `flutter doctor` and fix anything it flags. Useful extras: [VS Code](https://code.visualstudio.com/) with the [Flutter extension](https://marketplace.visualstudio.com/items?itemName=Dart-Code.flutter), [Postman](https://www.postman.com/downloads/) (or curl) for testing the API, and the [Flutter](https://docs.flutter.dev/) and [Flask](https://flask.palletsprojects.com/) docs.

## API setup

The API runs entirely in Docker. All configuration lives in `api/.env` (git-ignored — create it from the template below):

```env
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=mydatabase
DB_USER=myuser
DB_PASSWORD=mypassword
DB_NAME=mydatabase
DB_HOST=db
DB_PORT=5432
SECRET_KEY=change-me
PGADMIN_DEFAULT_EMAIL=admin@local.dev
PGADMIN_DEFAULT_PASSWORD=admin
```

Start everything:

```bash
cd api
docker compose up --build
```

- API: `http://localhost:5000`
- pgAdmin: `http://localhost:5050` (log in with the PGADMIN_* values above)

On first start the database tables are created and **seeded automatically** with the drone fleet (11 drones), the pilot registry (8 pilots), and one admin user. Seeding is idempotent — it only fills empty tables, so restarts never duplicate data.

**Seeded admin account (development only):** email `admin@terravia.africa`, password `123456`, role `admin`.

> ⚠️ `db.create_all()` never alters existing tables. If you change a model in `api/app/models.py`, reset the dev database: `docker compose down -v && docker compose up --build` (this wipes all data).

## Testing the API

From your PC, with the stack running:

**Login with the seeded admin** (returns a JWT valid for 30 minutes):

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@terravia.africa", "password": "123456"}'
```

**Access the protected route** (paste the token from the login response):

```bash
curl http://localhost:5000/ -H "x-access-token: <TOKEN>"
```

Expected: `{"message": "You have accessed a protected route!", "user": {...}}`

**Register a new user:**

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com", "password": "secret", "role": "pilot"}'
```

The token is sent via the `x-access-token` header on all protected routes. The seed data (drones, pilots) can be inspected through pgAdmin at `http://localhost:5050`.

## Flutter app setup

The app reads its API address from an `.env` file bundled as an asset.

1. Create `app/.env` (already git-ignored) pointing at your **PC's Wi-Fi IP**:

   ```
   API_BASE_URL=http://192.168.1.192:5000
   ```

   Find your IP with `ipconfig` (Windows) — look for the IPv4 address of your Wi-Fi adapter. `localhost` will not work: on a phone it refers to the phone itself.

2. Install dependencies:

   ```bash
   cd app
   flutter pub get
   ```

> After changing `app/.env`, rebuild the app — assets are baked in at build time, hot reload is not enough.

## Loading the Flutter app on your Android phone

1. **Open port 5000 in Windows Firewall** (one-time, admin PowerShell) so the phone can reach the API:

   ```powershell
   netsh advfirewall firewall add rule name="Terravia API dev" dir=in action=allow protocol=TCP localport=5000 profile=Private
   ```

2. Connect the phone via USB, accept the debugging prompt, and confirm it's detected:

   ```bash
   flutter devices
   ```

3. Run the app:

   ```bash
   flutter run
   ```

   This installs and launches the app in debug mode (hot reload enabled). For a standalone test build without a USB cable attached, use `flutter run --release`.

4. In the app, log in with `admin@terravia.africa` / `123456`.

### Troubleshooting

- **Can't reach the API from the phone:** open `http://<your-PC-IP>:5000/` in the phone's browser — you should see `{"error": "Token is missing! Log in first"}`. If it times out, check the firewall rule and that both devices are on the same Wi-Fi network (not a guest network). If your PC's IP changed (DHCP), update `app/.env` and rebuild.
- **API must be running:** `docker compose up` in `api/` before testing from the phone.
- Plain `http://` is allowed in the app for development (`usesCleartextTraffic="true"` in the Android manifest); use HTTPS when deploying beyond local development.

## Developer guide

### Adding a new API route

The workflow, illustrated with a drones endpoint in `api/app/routes/protected.py`:

1. **Model** — routes return rows from a model in `api/app/models.py` via its `to_dict()`. If you add a *new* model, the dev database must be reset (`docker compose down -v`) because `db.create_all()` doesn't alter existing tables.
2. **Route** — add a function to a blueprint. Protected routes stack two decorators: `@protected_bp.route(...)` for the URL and `@token_required` for auth, which decodes the JWT and passes `current_user` into your function. (`api/app/routes/auth.py` holds the public routes: register/login/logout.)

   ```python
   from app.middleware import token_required
   from app.models import Drone, db

   @protected_bp.route('/drones', methods=['GET'])
   @token_required
   def get_drones(current_user):
       drones = Drone.query.all()
       return jsonify([d.to_dict() for d in drones]), 200

   @protected_bp.route('/drones', methods=['POST'])
   @token_required
   def create_drone(current_user):
       data = request.get_json()
       drone = Drone(
           call_sign=data['call_sign'],
           model=data.get('model'),
           serial_number=data['serial_number'],
           max_flight_time=data.get('max_flight_time', 0),
           is_active=data.get('is_active', False),
           created_by=current_user.id,
       )
       db.session.add(drone)
       db.session.commit()
       return jsonify(drone.to_dict()), 201
   ```

   A new blueprint file additionally needs `app.register_blueprint(...)` in `api/app/__init__.py`.
3. **Rebuild** — the code is baked into the Docker image, so apply changes with `docker compose up --build` (if you iterate a lot, consider mounting the code as a volume in `docker-compose.yml`).
4. **Test** — same curl pattern as above, e.g. `curl http://localhost:5000/drones -H "x-access-token: <TOKEN>"`.

### Fetching data from the API in Flutter

All HTTP goes through `lib/api_service.dart` so the base URL, token header, and JSON handling live in one place. A typical method:

```dart
static Future<List<dynamic>> getDrones(String token) async {
  final response = await http.get(
    Uri.parse('$baseUrl/drones'),
    headers: {'Content-Type': 'application/json', 'x-access-token': token},
  );
  if (response.statusCode == 200) {
    return jsonDecode(response.body) as List<dynamic>;  // List of maps: d['call_sign'], ...
  }
  throw Exception('Failed to load drones (${response.statusCode})');
}
```

The token comes from `AuthProvider.token` after login — the same value curl sends in `x-access-token`.

### How Provider works

Provider is the bridge between state and UI. State lives in a class that extends `ChangeNotifier` (like `AuthProvider`); widgets subscribe to it and rebuild whenever `notifyListeners()` fires. Screens never fetch data themselves — they ask a provider, the provider calls the ApiService, then announces the change:

```
button press ──▶ Provider.fetchDrones(token)      state + notifyListeners()
                     │
                     ▼
                ApiService.getDrones(token)       HTTP, token header, JSON decoding
                     │  GET /drones + x-access-token
                     ▼
                Flask @token_required route       JWT check → current_user
                     │  SQLAlchemy
                     ▼
                PostGIS  ── rows travel back up ──▶ UI rebuilds with new data
```

Example provider for the drone list:

```dart
class DroneProvider with ChangeNotifier {
  List<dynamic> _drones = [];
  bool _loading = false;

  List<dynamic> get drones => _drones;
  bool get loading => _loading;

  Future<void> fetchDrones(String token) async {
    _loading = true;
    notifyListeners();   // UI shows the spinner
    try {
      _drones = await ApiService.getDrones(token);
    } finally {
      _loading = false;
      notifyListeners();   // UI shows the list
    }
  }
}
```

Register it in `main.dart`'s `MultiProvider`, trigger fetches with `Provider.of<DroneProvider>(context, listen: false)` (in callbacks/`initState`), and read state reactively with `Consumer<DroneProvider>` in `build`.

Two rules that prevent the classic bugs: trigger with `listen: false` so callbacks don't rebuild widgets, and after **any** `await`, guard `context` use with `if (!mounted) return;` — the widget may have been unmounted while the request was in flight (this is exactly what the login screen's `AuthWrapper` handoff does).

### Caching and offline operation

The app caches data in **SharedPreferences** — a small on-device key-value store that survives app restarts — so it can show data without waiting for, or even without having, a network connection. Currently two keys are cached: `token` (the JWT) and `user` (the user map as a JSON string). All of it lives in `lib/provider/auth_provider.dart`.

The lifecycle:

| Event | What happens to the cache |
|---|---|
| Successful login | `token` and `user` are written to prefs |
| App startup (`tryAutoLogin`) | cached values are adopted instantly, a live refresh is attempted, and the cache is rewritten if it succeeds |
| Logout | both keys are removed |

The design principle: **the network is the source of truth, the cache is the fallback.** `tryAutoLogin()` never blocks on the network — it optimistically signs in with the cached token/user, flags the session as offline (`isOfflineMode`, which drives the ⚠️ Offline banner on the home screen), then tries `GET /` in the background. On success the fresh user data replaces the cached copy; on failure the cached data keeps being served in offline mode.

> Activation: `tryAutoLogin()` only runs if it's invoked when the provider is created — add the cascade in `main.dart` or the cache is never read at startup:
>
> ```dart
> ChangeNotifierProvider(create: (_) => AuthProvider()..tryAutoLogin()),
> ```

**Reusing the pattern for other data** (cache-aside). To make any dataset offline-capable — say, the drone fleet — store a JSON snapshot under a stable key, serve it before the network call, then refresh and rewrite:

```dart
Future<void> fetchDrones(String token) async {
  final prefs = await SharedPreferences.getInstance();

  // 1. Serve the cache instantly (works fully offline)
  final cached = prefs.getString('drones');
  if (cached != null) {
    _drones = jsonDecode(cached);
    notifyListeners();
  }

  // 2. Refresh from the network
  try {
    _drones = await ApiService.getDrones(token);
    prefs.setString('drones', jsonEncode(_drones));   // 3. Rewrite the cache
    _offline = false;
  } catch (_) {
    _offline = true;   // keep whatever the cache gave us
  }
  notifyListeners();
}
```

Caveats worth knowing:

- SharedPreferences is plain text on disk — fine for development, but tokens should move to [`flutter_secure_storage`](https://pub.dev/packages/flutter_secure_storage) (encrypted Keystore storage) before production.
- An expired token (401) currently looks identical to "server unreachable" — both end in offline mode. To handle them differently, check the response status code and log out on 401s.
- Cached data never expires on its own; only logout clears it, and every successful refresh overwrites it.
