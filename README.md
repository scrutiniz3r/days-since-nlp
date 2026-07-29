# Days Since — Firebase Edition

Same app, new backend. This version replaces the GitHub Gist + PIN-only
storage with **Firebase Authentication + Firestore**, so sign-up is one tap
(Google) or a normal email/password form — no more copying Gist IDs and
tokens by hand.

Everything else — tiles, labels, notes, reminders, dark mode, the voice/NLP
logging pipeline (Cloudflare Worker + HuggingFace) — is unchanged. Only the
account and data-storage layer changed.

## What changed, technically

- **Auth:** Firebase Auth, with Google Sign-In as the primary path and
  email/password as a fallback. `onAuthStateChanged` is now the app's main
  gate (replacing the old "check localStorage for a Gist config" check).
- **Data storage:** Firestore, one document per user —
  `users/{uid} = { items: [...], labels: [...], settings: {...} }`.
  This mirrors the old Gist JSON shape almost exactly, which is why the vast
  majority of the app's existing render/action code needed **zero changes**
  — it already worked on an in-memory `data.items` / `data.labels` object;
  Firestore just replaced the Gist as where that blob is persisted.
- **Real-time sync:** a Firestore `onSnapshot` listener means changes made
  on one device now appear on another automatically — no manual "Sync"
  button needed anymore.
- **Onboarding:** shown once after signup, with a Firestore
  `settings.onboardingDone` flag. If a user somehow already has items but no
  flag (e.g. from a migration), onboarding is skipped automatically.
- **PIN:** still available as an *optional local lock* layered on top of
  Firebase auth (handy for shared devices) — it's no longer the only thing
  standing between someone and your data.

## A note on the data model — the honest tradeoff

Storing the whole tracker as one Firestore document (rather than one
document per item, per the fully "normalized" schema) is a deliberate
simplification: it kept the migration shippable by reusing almost all of
the existing app code untouched, and it's genuinely fine at this app's
scale — a personal tracker's entire JSON, even with years of history, stays
well under Firestore's 1MB document limit.

If you ever want true per-item writes (so editing one item doesn't rewrite
everyone else's data in the same request) or server-side querying
("show me everything logged in the last 7 days"), the natural next step is
splitting `items` into a `users/{uid}/items/{itemId}` subcollection, with
`history` split further into a `.../entries/{dateKey}` subcollection under
each item. That's a bigger rewrite of the render/save functions and wasn't
necessary for this pass.

## Setup

### 1. Create a Firebase project
Go to [console.firebase.google.com](https://console.firebase.google.com) →
Add project → follow the prompts (Analytics is optional, skip if unsure).

### 2. Register a Web app
Project Settings (gear icon) → General → Your apps → **Web** (`</>`) icon →
give it a nickname → Register app. Firebase shows you a config object —
copy it.

### 3. Paste your config into `index.html`
Near the top of the `<head>`, find:

```js
const firebaseConfig = {
  apiKey: "PASTE_YOUR_API_KEY",
  authDomain: "PASTE_YOUR_PROJECT.firebaseapp.com",
  projectId: "PASTE_YOUR_PROJECT_ID",
  storageBucket: "PASTE_YOUR_PROJECT.appspot.com",
  messagingSenderId: "PASTE_YOUR_SENDER_ID",
  appId: "PASTE_YOUR_APP_ID"
};
```

Replace each value with what Firebase gave you. This config is safe to
commit publicly — it identifies your project, it isn't a secret (security
comes from Firestore rules and Auth, not from hiding this).

### 4. Enable sign-in methods
Firebase Console → Build → Authentication → Get started → **Sign-in
method** tab → enable:
- **Google** (toggle on, pick a support email)
- **Email/Password** (toggle on)

### 5. Create the Firestore database
Firebase Console → Build → Firestore Database → Create database → start in
**production mode** → pick a region close to you.

### 6. Apply the security rules
Firestore → Rules tab → paste the contents of `firestore.rules` from this
repo → Publish. This ensures each user can only read/write their own
document — nobody can see anyone else's tracker.

### 7. Add your deployed domain to authorized domains
If deploying to GitHub Pages: Authentication → Settings → Authorized
domains → Add domain → `your-username.github.io`. (localhost is already
allowed by default for local testing.)

### 8. Deploy
Push to GitHub, enable GitHub Pages on the repo, done.

## Migrating existing data from the old Gist version

If you (or your users) were on the old Gist-based version, there's a
**Settings → Import from old Gist** option. It asks for the same Gist ID +
token as before, pulls the data, and merges any items/labels that aren't
already present into the new Firestore-backed account. It's additive —
it never deletes anything.
