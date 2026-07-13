# Adding the Demo Videos to the Website

## Step 1 — Upload to GitHub
1. Go to your site repo on GitHub → **Add file → Upload files**
2. Drag the whole `videos` folder (all 4 files: 2 MP4s + 2 poster JPGs) into the upload area
3. Commit. The files will live at `videos/family-demo.mp4` etc.

## Step 2 — Homepage (index.html): family video
Paste this where you want the video section (suggested: right before the "A Look Inside" sample gallery):

```html
<!-- Demo video -->
<section style="max-width:860px;margin:60px auto;padding:0 20px;text-align:center;">
  <h2 style="font-family:'Playfair Display',Georgia,serif;color:#16162A;">See it in two minutes</h2>
  <p style="color:#6B6B80;margin-bottom:24px;">The whole picture — one questionnaire, every audience.</p>
  <video controls preload="metadata" poster="videos/family-demo-poster.jpg"
         style="width:100%;border-radius:16px;box-shadow:0 12px 40px rgba(22,22,42,.18);">
    <source src="videos/family-demo.mp4" type="video/mp4">
  </video>
</section>
```

## Step 3 — Partnerships page (partnerships.html): provider video
Paste this near the top, after the hero (suggested: right before "Why partner"):

```html
<!-- Provider demo video -->
<section style="max-width:860px;margin:60px auto;padding:0 20px;text-align:center;">
  <h2 style="font-family:'Playfair Display',Georgia,serif;color:#16162A;">Watch the two-minute walkthrough</h2>
  <video controls preload="metadata" poster="videos/provider-demo-poster.jpg"
         style="width:100%;border-radius:16px;box-shadow:0 12px 40px rgba(22,22,42,.18);">
    <source src="videos/provider-demo.mp4" type="video/mp4">
  </video>
</section>
```

## Notes
- Videos are web-optimized (7-8 MB each, streams immediately — no full download wait).
- `controls` + no autoplay is intentional: these are voice-driven, and browsers block autoplay with sound anyway.
- If you'd rather I insert these into the pages for you, just say so and I'll produce updated copies of index.html and partnerships.html ready to upload.
