#!/bin/bash
# Systematic Test Fixes for Project Reorganization
# This script automatically fixes import paths in test files

echo "Starting test fixes for project reorganization..."

# 1. Update imports in test_app.py
echo "Fixing test_app.py..."
sed -i '' 's/from app import/from itinerary_generator.app import/g' tests/test_app.py
sed -i '' 's/patch(.app\./patch(.itinerary_generator.app\./g' tests/test_app.py
sed -i '' 's/patch(\"app\./patch(\"itinerary_generator.app\./g' tests/test_app.py

# 2. Update imports in test_parser.py
echo "Fixing test_parser.py..."
sed -i '' 's/from parser import/from itinerary_generator.parser import/g' tests/test_parser.py
SAMPLE_DATA_PATH='SAMPLE_DATA_PATH = os.path.join("itinerary_generator", "data", "samples", "trip.sample.json")\n'
sed -i '' "/import pytest/a\\
$SAMPLE_DATA_PATH
" tests/test_parser.py
sed -i '' 's/load_trip_data("static\/trip.sample.json")/load_trip_data(SAMPLE_DATA_PATH)/g' tests/test_parser.py

# 3. Update imports in test_formatting.py
echo "Fixing test_formatting.py..."
sed -i '' 's/from parser import/from itinerary_generator.parser import/g' tests/test_formatting.py
sed -i '' 's/from formatting import/from itinerary_generator.formatting import/g' tests/test_formatting.py

# 4. Update imports in test_lookups.py
echo "Fixing test_lookups.py..."
sed -i '' 's/from lookups import/from itinerary_generator.lookups import/g' tests/test_lookups.py

# 5. Update imports in test_renderer.py
echo "Fixing test_renderer.py..."
sed -i '' 's/from renderer import/from itinerary_generator.renderer import/g' tests/test_renderer.py

# 6. Update imports in test_renderer_convert_to_pdf.py
echo "Fixing test_renderer_convert_to_pdf.py..."
sed -i '' 's/from renderer import/from itinerary_generator.renderer import/g' tests/test_renderer_convert_to_pdf.py

# 7. Update imports in test_generate_itinerary.py
echo "Fixing test_generate_itinerary.py..."
sed -i '' 's/from generate_itinerary import/from itinerary_generator.generate_itinerary import/g' tests/test_generate_itinerary.py
sed -i '' 's/patch(.generate_itinerary\./patch(.itinerary_generator.generate_itinerary\./g' tests/test_generate_itinerary.py
sed -i '' 's/patch(\"generate_itinerary\./patch(\"itinerary_generator.generate_itinerary\./g' tests/test_generate_itinerary.py

# 8. Update imports in test_integration.py
echo "Fixing test_integration.py..."
sed -i '' 's/from generate_itinerary import/from itinerary_generator.generate_itinerary import/g' tests/test_integration.py

# 9. Update conftest.py
echo "Fixing conftest.py..."
SAMPLE_DATA_PATH='SAMPLE_DATA_PATH = os.path.join("itinerary_generator", "data", "samples", "trip.sample.json")\n'
sed -i '' "/import pytest/a\\
$SAMPLE_DATA_PATH
" tests/conftest.py
sed -i '' 's/with open("static\/trip.sample.json", "r") as f:/with open(SAMPLE_DATA_PATH, "r") as f:/g' tests/conftest.py

# 10. Create symbolic links for backward compatibility (as a fallback)
echo "Creating backup symbolic links for compatibility..."
mkdir -p static
mkdir -p itinerary_generator/data/samples

# Copy sample files if they don't exist
if [ ! -f itinerary_generator/data/samples/trip.sample.json ]; then
    cp static/trip.sample.json itinerary_generator/data/samples/ 2>/dev/null || echo "Warning: No trip.sample.json found"
fi

if [ ! -f itinerary_generator/data/samples/template.sample.html ]; then
    cp static/template.sample.html itinerary_generator/data/samples/ 2>/dev/null || echo "Warning: No template.sample.html found"
fi

# Create symbolic links for backward compatibility
ln -sf itinerary_generator/app.py app.py 2>/dev/null || true
ln -sf itinerary_generator/parser.py parser.py 2>/dev/null || true
ln -sf itinerary_generator/formatting.py formatting.py 2>/dev/null || true
ln -sf itinerary_generator/lookups.py lookups.py 2>/dev/null || true
ln -sf itinerary_generator/renderer.py renderer.py 2>/dev/null || true
ln -sf itinerary_generator/generate_itinerary.py generate_itinerary.py 2>/dev/null || true
ln -sf itinerary_generator/data/samples/trip.sample.json static/trip.sample.json 2>/dev/null || true
ln -sf itinerary_generator/data/samples/template.sample.html static/template.sample.html 2>/dev/null || true

echo "Test fixes complete!"
echo "Try running 'make test' again"
