source "https://rubygems.org"

# Use the github-pages gem to match the exact Jekyll + plugin versions
# that GitHub Pages runs in production. Local builds will then match
# what users see at https://barefootbetters.github.io/scooby-engine/.
#
# Update with: bundle update github-pages
gem "github-pages", group: :jekyll_plugins

# Windows + JRuby compatibility shims (no-op on Linux/macOS)
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", "~> 2.0"
  gem "tzinfo-data"
end
