# Apple Design Guidelines Reference

## Overview
This document provides quick access to Apple's design standards and guidelines for creating applications and web interfaces that align with Apple's design philosophy.

## Primary Resources

### Apple Human Interface Guidelines (HIG)
**URL:** https://developer.apple.com/design/human-interface-guidelines/

The HIG is Apple's comprehensive resource for designing apps across all Apple platforms. It provides detailed guidance on:
- Design principles and best practices
- Platform-specific guidelines
- Component specifications
- Interaction patterns
- Visual design standards

### Platform-Specific Guidelines

#### macOS
- **Section:** Platforms → macOS
- **Focus Areas:**
  - Window management and hierarchy
  - Menu bar and toolbar design
  - Sidebar and navigation patterns
  - Native controls and components
  - System integration features

#### iOS/iPadOS
- **Section:** Platforms → iOS
- **Key Topics:**
  - Touch-first interface design
  - Navigation patterns
  - Gesture-based interactions
  - Adaptive layouts

## Design Resources

### Apple Design Resources
**URL:** https://developer.apple.com/design/resources/

**Available Downloads:**
- Design templates for Sketch, Figma, Adobe XD
- Production templates for Final Cut Pro and Motion
- Reality Composer templates
- Keynote themes

### Typography
**System Fonts:**
- **SF Pro** - The default font for macOS and iOS
  - SF Pro Display (20pt and larger)
  - SF Pro Text (19pt and smaller)
- **SF Mono** - Monospaced variant for code
- **New York** - Serif font option

**Download:** Available through Apple Design Resources

### Iconography
**SF Symbols:** https://developer.apple.com/sf-symbols/
- 5,000+ configurable symbols
- Multiple weights and scales
- Built-in accessibility features
- Free SF Symbols app for browsing

## Key Design Principles

### Visual Design
1. **Clarity** - Content is paramount; UI should never compete
2. **Deference** - UI helps people understand and interact with content
3. **Depth** - Visual layers and realistic motion convey hierarchy

### Layout Fundamentals
- **Grid System:** 8pt spacing grid
- **Safe Areas:** Respect system UI elements
- **Margins:** Consistent spacing (typically 20pt on macOS)
- **Alignment:** Left-aligned text for LTR languages

### Color
- **System Colors:** Use semantic colors that adapt to Light/Dark mode
- **Accent Colors:** Customizable but should respect system preferences
- **Contrast Ratios:** Meet WCAG accessibility standards

### macOS-Specific Patterns
- **Translucency:** Window backgrounds with vibrancy
- **Traffic Light Controls:** Standard window controls
- **Sidebars:** 
  - Minimum width: 150pt
  - Maximum width: 300-400pt (depending on content)
- **Toolbars:** Height of 38pt (regular) or 28pt (compact)

## Applying to Web Development

While Apple doesn't provide specific web guidelines, you can apply HIG principles:

### CSS Framework Considerations
```css
/* Example: Implementing Apple-like design tokens */
:root {
  /* Typography */
  --font-body: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif;
  --font-display: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
  --font-mono: "SF Mono", Monaco, "Cascadia Mono", "Roboto Mono", monospace;
  
  /* Spacing (8pt grid) */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  
  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  
  /* Colors (Light Mode) */
  --color-background: #ffffff;
  --color-surface: #f5f5f7;
  --color-text-primary: #1d1d1f;
  --color-text-secondary: #86868b;
  --color-accent: #0071e3;
}

/* Dark Mode */
@media (prefers-color-scheme: dark) {
  :root {
    --color-background: #000000;
    --color-surface: #1c1c1e;
    --color-text-primary: #f5f5f7;
    --color-text-secondary: #86868b;
  }
}
```

### Component Patterns
- **Buttons:** Rounded corners (6-8px), clear hover states
- **Cards:** Subtle shadows, clean borders
- **Navigation:** Fixed or sticky positioning
- **Forms:** Clear labels, generous touch targets (44x44pt minimum)

## Best Practices

### Do's
- ✅ Use system fonts for better performance and consistency
- ✅ Support both Light and Dark modes
- ✅ Implement smooth animations (ease-in-out, 200-300ms)
- ✅ Respect user preferences (reduced motion, contrast)
- ✅ Use semantic HTML for better accessibility

### Don'ts
- ❌ Override system UI unnecessarily
- ❌ Use custom scrollbars unless essential
- ❌ Ignore platform conventions
- ❌ Create UI that looks identical across platforms

## Additional Resources

### Documentation
- **Accessibility:** https://developer.apple.com/accessibility/
- **App Store Guidelines:** https://developer.apple.com/app-store/review/guidelines/
- **Marketing Guidelines:** https://developer.apple.com/app-store/marketing/guidelines/

### Tools
- **SF Symbols App:** Browse and export symbols
- **Reality Converter:** Convert 3D models
- **Create ML:** Machine learning model creation

### Community
- **Apple Developer Forums:** https://developer.apple.com/forums/
- **WWDC Videos:** https://developer.apple.com/videos/
- **Design Awards:** Examples of excellence in design

## Quick Reference Checklist

When designing for Apple platforms:
- [ ] Using system fonts (SF Pro family)
- [ ] Following 8pt spacing grid
- [ ] Supporting Light/Dark modes
- [ ] Meeting accessibility standards
- [ ] Respecting safe areas
- [ ] Using semantic colors
- [ ] Implementing native interaction patterns
- [ ] Testing on actual devices

## Update Notes
- Last updated: June 2025
- Check Apple Developer site for latest guidelines
- Major updates typically announced at WWDC (June)