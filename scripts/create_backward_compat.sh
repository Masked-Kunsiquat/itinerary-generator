#!/bin/bash
# Create backward compatibility links to help with the transition
# These should be removed once tests are properly updated

# Create directory if doesn't exist
mkdir -p static

# Remove any existing files or links
rm -f app.py parser.py formatting.py lookups.py renderer.py generate_itinerary.py
rm -f static/trip.sample.json static/template.sample.html

# Create symbolic links for Python modules
ln -sf itinerary_generator/app.py app.py
ln -sf itinerary_generator/parser.py parser.py
ln -sf itinerary_generator/formatting.py formatting.py
ln -sf itinerary_generator/lookups.py lookups.py
ln -sf itinerary_generator/renderer.py renderer.py
ln -sf itinerary_generator/generate_itinerary.py generate_itinerary.py

# Create symbolic links for data files
ln -sf itinerary_generator/data/samples/trip.sample.json static/trip.sample.json
ln -sf itinerary_generator/data/samples/template.sample.html static/template.sample.html

echo "Backward compatibility links created!"
echo "Warning: These are temporary and should be removed after tests are updated."
