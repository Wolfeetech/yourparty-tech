# YourParty.tech - Professionelles Design System v3.0

## 🎯 Design-Prinzipien

1. **Fokus auf Radio Live-Stream** - Hauptfeature prominent platziert
2. **Klare visuelle Hierarchie** - Wichtigstes zuerst
3. **CI-Farben konsequent** - Emerald (#2E8B57) als Primary
4. **Minimalistisch & Modern** - Kein Overdesign
5. **Mobile-First** - Optimiert für alle Geräte

## 🎨 Farb-System (YourParty CI)

```css
Primary:     #2E8B57 (Emerald Green)
Secondary:   #800080 (Purple)
Accent:      #CC5500 (Terracotta)
Neutral:     #F4EFEA (Beige)

Backgrounds:
- Dark:      #0a0a0a
- Card:      #1a1a1a
- Elevated:  #242424

Text:
- Primary:   #ffffff
- Secondary: #9ca3af
- Tertiary:  #6b7280
```

## 📐 Layout-Struktur

### 1. **Header** (Sticky, 60px)
- Logo links (Gradient: Emerald → Purple)
- Navigation rechts (Desktop)
- Burger-Menu (Mobile)
- Backdrop-blur: 20px

### 2. **Hero Section** (100vh)
- Zentrierter Text
- Headline: 64px (Display Font)
- CTA Buttons: Primary + Ghost
- Scroll-Indicator

### 3. **Radio Live Section** (Hauptfeature)
**Desktop Layout (1200px+):**
```
[------300px Artwork------] [------1fr Meta------] [------340px History------]
```

**Tablet (768-1199px):**
```
[------340px Artwork------] [------1fr Meta------]
[------History (full width)------]
```

**Mobile (<768px):**
```
[------Artwork (zentriert)------]
[------Meta------]
[------History------]
```

### 4. **Content Sections**
- USP Grid: 3 Spalten (Auto-fit)
- Services: 2 Spalten
- References: Carousel
- Footer: 3 Spalten

## 🔤 Typografie

**Display Font:** Space Grotesk (800, 700, 600)
- Headlines
- Brand
- CTAs

**Body Font:** Inter (800, 700, 600, 500, 400)
- Fließtext
- Navigation
- UI Elements

**Hierarchy:**
```
H1: 64px / 800 / -0.02em
H2: 48px / 800 / -0.01em
H3: 32px / 700 / 0
Body: 16px / 500 / 0.01em
Small: 14px / 500
Tiny: 12px / 600 (Labels/Eyebrows)
```

## 📱 Responsive Breakpoints

```css
Mobile:  320-767px
Tablet:  768-1199px
Desktop: 1200px+
Wide:    1400px+
```

## 🎭 Komponenten

### Radio Player Card
```
Artwork: 300x300px (Desktop)
Meta:
  - Artist: 13px, UPPERCASE, Emerald
  - Title: 40px, Display Font, Bold
  - Album: 15px, Muted
  - LIVE Badge: Emerald BG, pulse animation
  - Listener Count: Icon + Number
  - Rating Stars: 28px, Emerald on active

Play Button:
  - Size: 72x72px
  - Position: Bottom-right auf Artwork
  - Border: 4px white
  - Gradient: Emerald → Dark Emerald
  - Shadow: 0 8px 24px rgba(46,139,87,0.4)
  - Hover: Scale(1.1) + Shadow increase
```

### History List
```
Item: 52x52px Cover + Info
- Title: 14px, 600
- Artist: 13px, Muted
- Hover: translateX(3px) + background change
- Max-Height: 520px
- Scrollbar: 4px, Emerald
```

### Buttons
```
Primary:
  - Background: Gradient (Emerald → Dark)
  - Padding: 14px 32px
  - Border-radius: 24px
  - Shadow: Glow effect
  - Hover: translateY(-2px)

Ghost:
  - Border: 1px rgba(255,255,255,0.1)
  - Hover: Border Emerald
```

## 🔄 Animationen

```css
Transitions: 0.2-0.3s ease-out
Hover Transforms: translateY, scale, translateX
Micro-animations: Stars (pop), LIVE badge (pulse)
Scroll-reveals: fadeSlideUp (0.8s)
```

## 📏 Spacing System

```css
Base: 4px

XS:  4px   (gap-1)
S:   8px   (gap-2)
M:   12px  (gap-3)
L:   16px  (gap-4)
XL:  24px  (gap-6)
2XL: 32px  (gap-8)
3XL: 48px  (gap-12)
4XL: 64px  (gap-16)
5XL: 80px  (gap-20)
```

## 🎯 UX Best Practices

1. **Kontrast:** Minimum 4.5:1 für Text
2. **Touch Targets:** Minimum 44x44px
3. **Focus States:** Alle interaktiven Elemente
4. **Loading States:** Skeleton screens
5. **Error States:** Klare Fehlermeldungen
6. **Accessibility:** ARIA labels, semantic HTML

## 📦 Dateistruktur

```
wp-theme/yourparty-tech/
├── style.css              (Main stylesheet)
├── functions.php          (Theme setup)
├── header.php             (Global header)
├── footer.php             (Global footer)
├── front-page.php         (Homepage)
├── assets/
│   ├── app.js             (Interactive features)
│   └── (icons, images)
├── inc/
│   ├── content-config.php (SSOT for text)
│   ├── api.php            (REST endpoints)
│   └── customizer.php     (WordPress customizer)
└── template-parts/
    └── sections/
        ├── services.php
        ├── references.php
        └── about.php
```

## 🚀 Performance

- **CSS:** Minified, 12KB
- **Images:** WebP, lazy-loading
- **Fonts:** Preload critical fonts
- **JS:** Defer non-critical scripts
- **Caching:** Browser + CDN ready

---

**Erstellt:** 2025-11-27
**Version:** 3.0.0
**Status:** In Umsetzung
