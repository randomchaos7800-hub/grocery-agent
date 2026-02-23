"""
Seed Walmart purchase history (Sep 2025 – Feb 2026) into purchase_history table.
Run once: python3 seed_history.py
Items marked as returned are excluded.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "grocery.db"

# Each entry: (purchased_at, name, quantity, category, order_total)
# order_total is the full order amount; NULL for individual in-store items without full context
HISTORY = [
    # ─── SEP 7, 2025 — Store delivery $296.43 ───────────────────────────────
    ("2025-09-07", "Lay's Classic Potato Snack Chips 1oz 10ct", "1", "snacks", 296.43),
    ("2025-09-07", "Franz Cluster Hamburger Buns 15oz 8ct", "1", "bread", 296.43),
    ("2025-09-07", "MiO Vitamins Orange Vanilla Water Enhancer 1.62oz", "2", "drinks", 296.43),
    ("2025-09-07", "Jack's Frozen Meat Pizza Supreme 15.8oz", "1", "frozen", 296.43),
    ("2025-09-07", "Ghirardelli Milk Chocolate Baking Chips 11.5oz", "1", "baking", 296.43),
    ("2025-09-07", "Totino's Combination Pizza Rolls 50ct", "1", "frozen", 296.43),
    ("2025-09-07", "Tropicana Classic Lemonade 46oz", "2", "drinks", 296.43),
    ("2025-09-07", "Tropicana Strawberry Lemonade 46oz", "1", "drinks", 296.43),
    ("2025-09-07", "Tillamook Extra Creamy Unsalted Butter Sticks 4ct 16oz", "1", "dairy", 296.43),
    ("2025-09-07", "Kerrygold Naturally Softer Irish Butter 8oz Tub", "1", "dairy", 296.43),
    ("2025-09-07", "Great Value Sweetened Condensed Milk 14oz", "2", "baking", 296.43),
    ("2025-09-07", "Totino's Party Pizza Pack Combination 4ct", "1", "frozen", 296.43),
    # Sep 11 online (same order)
    ("2025-09-11", "BISSELL PowerClean FurFinder Cordless Vacuum", "1", "household", 296.43),
    ("2025-09-11", "3-Year Home Protection Plan $150-$199", "1", "household", 296.43),

    # ─── SEP 13, 2025 — Store delivery $194.77 ──────────────────────────────
    ("2025-09-13", "MiO Vitamins Orange Tangerine Water Enhancer 3.24oz", "1", "drinks", 194.77),
    ("2025-09-13", "Lucas Oil High Mileage Oil Stabilizer 1qt", "1", "auto", 194.77),
    ("2025-09-13", "Rice Krispies Treats Original 12.4oz 16ct", "1", "snacks", 194.77),
    ("2025-09-13", "Bar Keepers Friend Soft Cleanser 26oz", "1", "cleaning", 194.77),
    ("2025-09-13", "Tropicana Strawberry Lemonade 46oz", "2", "drinks", 194.77),
    ("2025-09-13", "Tropicana Classic Lemonade 46oz", "1", "drinks", 194.77),
    ("2025-09-13", "Dial Cherry Blossom Liquid Hand Soap 7.5oz", "2", "health", 194.77),
    ("2025-09-13", "Darigold Whole Lactose Free Ultra Filtered Milk 59oz", "1", "dairy", 194.77),
    ("2025-09-13", "Freshpet Dog Food Multi-Protein Recipe 3lb", "2", "pet", 194.77),
    ("2025-09-13", "Great Value Everyday Spoons White Cutlery 48ct", "1", "household", 194.77),
    ("2025-09-13", "Nature Valley Sweet & Salty Cashew Granola Bars 7.2oz", "2", "snacks", 194.77),
    ("2025-09-13", "Zesta Original Saltine Crackers 16oz", "1", "snacks", 194.77),
    ("2025-09-13", "Ore-Ida Crispy Tater Tots Value Size 5lb", "1", "frozen", 194.77),
    ("2025-09-13", "Ore-Ida Crispy Crinkles French Fried Potatoes 32oz", "1", "frozen", 194.77),
    ("2025-09-13", "Ore-Ida Classic Thick Cut Steak Fries 28oz", "1", "frozen", 194.77),
    ("2025-09-13", "Tillamook Extra Creamy Unsalted Butter Sticks 4ct 16oz", "1", "dairy", 194.77),
    ("2025-09-13", "Darigold Whole Milk Half Gallon 64oz", "1", "dairy", 194.77),
    ("2025-09-13", "Tillamook Extra Sharp Cheddar Cheese Block 8oz", "1", "dairy", 194.77),
    ("2025-09-13", "Tillamook Colby Jack Cheese Block 16oz", "1", "dairy", 194.77),
    ("2025-09-13", "Tillamook Pepper Jack Cheese Block 16oz", "1", "dairy", 194.77),
    ("2025-09-13", "Jumbo Russet Potatoes 8lb", "1", "produce", 194.77),
    ("2025-09-13", "Classico Tomato & Basil Pasta Sauce 24oz", "1", "pantry", 194.77),
    ("2025-09-13", "Mrs. T's Classic Cheddar Pierogies Family Size 24ct", "1", "frozen", 194.77),
    ("2025-09-13", "Great Value Fruit Punch Drink Enhancer 3.11oz", "3", "drinks", 194.77),
    ("2025-09-13", "McCormick Pure Ground Black Pepper 3oz", "1", "spices", 194.77),
    ("2025-09-13", "Freshness Guaranteed Sliced Italian Bread 14oz", "1", "bread", 194.77),
    # Sep 17 online (same order)
    ("2025-09-17", "Windex Electronics Wipes 25ct", "2", "household", 194.77),

    # ─── SEP 15, 2025 — Online delivery $56.39 (old address) ────────────────
    ("2025-09-15", "Equate Original 12-Hour Nasal Spray Max Strength 1oz", "2", "health", 56.39),
    ("2025-09-15", "Bentgo All-in-One Glass Salad Container 5-Compartment", "1", "household", 56.39),
    ("2025-09-15", "Crunch Pak Fresh Organic Peeled Sliced Apples 12oz", "1", "produce", 56.39),
    ("2025-09-15", "Great Value Fruit Punch Drink Enhancer 3.11oz", "1", "drinks", 56.39),
    ("2025-09-15", "MiO Vitamins Orange Vanilla Water Enhancer 1.62oz", "1", "drinks", 56.39),
    ("2025-09-15", "Marketside Caesar Bacon Chopped Salad Kit 10.2oz", "2", "produce", 56.39),

    # ─── SEP 26, 2025 — Store delivery $206.55 ──────────────────────────────
    ("2025-09-26", "Honey Nut Cheerios Family Size 18.8oz", "1", "cereal", 206.55),
    ("2025-09-26", "Fresh Blueberries 18oz", "1", "produce", 206.55),
    ("2025-09-26", "Freshness Guaranteed Carrot Cake Square 7.25oz", "2", "bakery", 206.55),
    ("2025-09-26", "Fresh Broccoli Crowns", "2", "produce", 206.55),
    ("2025-09-26", "Equate Enema Sodium Phosphates Saline Laxative 4.5oz 6ct", "1", "health", 206.55),
    ("2025-09-26", "Equate Original 12-Hour Nasal Spray Max Strength 1oz", "3", "health", 206.55),
    ("2025-09-26", "Freshpet Dog Food Multi-Protein Recipe 3lb", "2", "pet", 206.55),
    ("2025-09-26", "Freshness Guaranteed 5-Inch Chocolate Cake 15.9oz", "1", "bakery", 206.55),
    ("2025-09-26", "Rosarita Spicy Jalapeno Refried Beans 16oz", "1", "pantry", 206.55),
    ("2025-09-26", "Mission Super Soft Flour Tortillas Burrito Size 8ct", "1", "bread", 206.55),
    ("2025-09-26", "Tropicana Strawberry Lemonade 46oz", "1", "drinks", 206.55),
    ("2025-09-26", "Tropicana Classic Lemonade 46oz", "3", "drinks", 206.55),
    ("2025-09-26", "Morton Kosher Salt Coarse 16oz", "1", "spices", 206.55),
    ("2025-09-26", "Farmland Cooked Cubed Ham 1lb", "1", "meat", 206.55),
    ("2025-09-26", "MiO Vitamins Orange Vanilla Water Enhancer 1.62oz", "2", "drinks", 206.55),
    ("2025-09-26", "Great Value Fruit Punch Drink Enhancer 3.11oz", "1", "drinks", 206.55),
    ("2025-09-26", "Kerrygold Naturally Softer Irish Butter 8oz Tub", "2", "dairy", 206.55),
    ("2025-09-26", "Great Value Cream Cheese Brick 8oz", "1", "dairy", 206.55),
    ("2025-09-26", "Tillamook Extra Creamy Unsalted Butter Sticks 4ct", "1", "dairy", 206.55),
    ("2025-09-26", "Darigold Whole Lactose Free Ultra Filtered Milk 59oz", "2", "dairy", 206.55),
    ("2025-09-26", "Tillamook Extra Sharp Cheddar Cheese Block 8oz", "1", "dairy", 206.55),
    ("2025-09-26", "Tillamook Sharp Cheddar Cheese Block 8oz", "1", "dairy", 206.55),
    ("2025-09-26", "Tillamook Pepper Jack Cheese Block 8oz", "1", "dairy", 206.55),
    ("2025-09-26", "Marketside Caesar Bacon Chopped Salad Kit 10.2oz", "2", "produce", 206.55),
    ("2025-09-26", "New York Bakery Texas Toast Garlic & Butter Croutons 5oz", "1", "bread", 206.55),
    ("2025-09-26", "Tillamook Cultured Sour Cream 16oz", "1", "dairy", 206.55),
    ("2025-09-26", "Bush's Chili Beans Pinto in Mild Chili Sauce 16oz", "2", "pantry", 206.55),
    ("2025-09-26", "Bush's Chili Beans Kidney in Mild Chili Sauce 16oz", "2", "pantry", 206.55),
    ("2025-09-26", "Princella Sweet Potatoes Cut Yams in Syrup 40oz", "1", "pantry", 206.55),
    ("2025-09-26", "Great Value Pork Boneless Cooked Smoked Ham Steaks 2-Pack 14oz", "1", "meat", 206.55),
    ("2025-09-26", "Great Value Great Northern Beans 1lb", "2", "pantry", 206.55),

    # ─── OCT 5, 2025 — Store delivery $233.49 ───────────────────────────────
    ("2025-10-05", "SunChips Minis Garden Salsa 2-pack 3.75oz", "1", "snacks", 233.49),
    ("2025-10-05", "Better Homes & Gardens Cashmere Teak Wooden Wick Candle 13oz", "1", "home", 233.49),
    ("2025-10-05", "Better Homes & Gardens Red Apple Cedar Wooden Wick Candle 13oz", "1", "home", 233.49),
    ("2025-10-05", "Classico Tomato & Basil Pasta Sauce 24oz", "2", "pantry", 233.49),
    ("2025-10-05", "Crunch 'n Munch Buttery Toffee Popcorn with Peanuts 6oz", "2", "snacks", 233.49),
    ("2025-10-05", "Crunch Pak Fresh Organic Peeled Sliced Apples 12oz", "1", "produce", 233.49),
    ("2025-10-05", "Darigold Whole Lactose Free Ultra Filtered Milk 59oz", "1", "dairy", 233.49),
    ("2025-10-05", "Darigold Whole Milk Half Gallon 64oz", "1", "dairy", 233.49),
    ("2025-10-05", "Ferrero Rocher Premium Milk Hazelnut Chocolate Squares 3.7oz", "1", "snacks", 233.49),
    ("2025-10-05", "Fresh Green Onions Bunch", "1", "produce", 233.49),
    ("2025-10-05", "Freshpet Dog Food Multi-Protein Recipe 3lb", "2", "pet", 233.49),
    ("2025-10-05", "Hershey Assorted Halloween Candy 19.62oz 60ct", "1", "snacks", 233.49),
    ("2025-10-05", "Honey Ohs! Family Size Cereal 20oz", "1", "cereal", 233.49),
    ("2025-10-05", "Jocko Mölk Chocolate Protein Powder 21 Servings", "1", "health", 233.49),
    ("2025-10-05", "Jumbo Russet Potatoes 8lb", "1", "produce", 233.49),
    ("2025-10-05", "Kerrygold Naturally Softer Irish Butter 8oz Tub", "2", "dairy", 233.49),
    ("2025-10-05", "Kraft Grated Parmesan Romano & Asiago Cheese Shaker 8oz", "1", "dairy", 233.49),
    ("2025-10-05", "Litehouse Old Fashioned Caramel Dip Snack Size 6ct 2oz", "1", "snacks", 233.49),
    ("2025-10-05", "Marketside Fresh Organic Bananas Bunch", "1", "produce", 233.49),
    ("2025-10-05", "MiO Vitamins Orange Vanilla Water Enhancer 1.62oz", "3", "drinks", 233.49),
    ("2025-10-05", "Ore-Ida Classic Thick Cut Steak Fries 28oz", "1", "frozen", 233.49),
    ("2025-10-05", "Pork Belly Sliced Boneless ~1.5lb", "1", "meat", 233.49),
    ("2025-10-05", "Tabasco Original Red Pepper Sauce 2oz", "1", "condiments", 233.49),
    ("2025-10-05", "Tillamook Old-Fashioned Vanilla Ice Cream 48oz", "1", "frozen", 233.49),
    ("2025-10-05", "Tropicana Classic Lemonade 46oz", "3", "drinks", 233.49),
    ("2025-10-05", "Tropicana Strawberry Lemonade 46oz", "1", "drinks", 233.49),
    ("2025-10-05", "Tyson Oven Roasted Diced Chicken Breast 22oz Frozen", "1", "frozen", 233.49),
    ("2025-10-05", "bettergoods Bronze Cut Bucatini Pasta 16oz", "1", "pantry", 233.49),
    ("2025-10-05", "bettergoods Bronze Cut Fusilli Bucati Pasta 16oz", "1", "pantry", 233.49),
    ("2025-10-05", "bettergoods Bronze Cut Trompetti Pasta 16oz", "1", "pantry", 233.49),

    # ─── OCT 12, 2025 — Store delivery $153.48 ──────────────────────────────
    ("2025-10-12", "Bob Evans Gluten-Free Original Mashed Potatoes 12oz 2ct", "2", "frozen", 153.48),
    ("2025-10-12", "Crunch Pak Fresh Organic Peeled Sliced Apples 12oz", "1", "produce", 153.48),
    ("2025-10-12", "Finish Jet-Dry Rinse Aid 23oz", "1", "household", 153.48),
    ("2025-10-12", "Freshness Guaranteed Sliced Italian Bread 14oz", "1", "bread", 153.48),
    ("2025-10-12", "Great Value Naturally Hickory Smoked Sliced Bacon 12oz", "1", "meat", 153.48),
    ("2025-10-12", "Kerrygold Naturally Softer Irish Butter 8oz Tub", "2", "dairy", 153.48),
    ("2025-10-12", "Marketside Caesar Bacon Chopped Salad Kit 10.2oz", "1", "produce", 153.48),
    ("2025-10-12", "Marketside Italian Creme Bar Cake 35oz Refrigerated", "1", "bakery", 153.48),
    ("2025-10-12", "Marketside Ready to Heat Tonkatsu Ramen Bowl 14oz", "1", "pantry", 153.48),
    ("2025-10-12", "MiO Vitamins Orange Vanilla Water Enhancer 1.62oz", "2", "drinks", 153.48),
    ("2025-10-12", "Ore-Ida Classic Thick Cut Steak Fries 28oz", "1", "frozen", 153.48),
    ("2025-10-12", "QuickSteak 100% Thin Sirloin Frozen Beef 10.8oz", "1", "frozen", 153.48),
    ("2025-10-12", "Stove Top Stuffing Mix Chicken Twin Pack 12oz", "1", "pantry", 153.48),
    ("2025-10-12", "SunChips Minis Garden Salsa 3.75oz", "1", "snacks", 153.48),
    ("2025-10-12", "Tillamook Extra Creamy Unsalted Butter Sticks 4ct 16oz", "1", "dairy", 153.48),
    ("2025-10-12", "Tropicana Classic Lemonade 46oz", "2", "drinks", 153.48),
    ("2025-10-12", "Tropicana Strawberry Lemonade 46oz", "1", "drinks", 153.48),
    ("2025-10-12", "bettergoods Garlic Butter Flavored Seasoning 3oz", "1", "spices", 153.48),

    # ─── OCT 19, 2025 — Store delivery $164.81 ──────────────────────────────
    ("2025-10-19", "Marketside Brioche Slider Rolls 16.9oz 12ct", "1", "bread", 164.81),
    ("2025-10-19", "BelGioioso Parmesan Cheese Wedge 8oz", "1", "dairy", 164.81),
    ("2025-10-19", "Cento Tomato Paste 4.56oz", "1", "pantry", 164.81),
    ("2025-10-19", "Classico Tomato & Basil Pasta Sauce 24oz", "1", "pantry", 164.81),
    ("2025-10-19", "Crunch Pak Fresh Organic Peeled Sliced Apples 12oz", "1", "produce", 164.81),
    ("2025-10-19", "Darigold Whole Lactose Free Ultra Filtered Milk 59oz", "1", "dairy", 164.81),
    ("2025-10-19", "Darigold Whole Milk Half Gallon 64oz", "1", "dairy", 164.81),
    ("2025-10-19", "El Monterey Extra Crunchy Beef & Cheese Taquitos 18ct 20.7oz", "1", "frozen", 164.81),
    ("2025-10-19", "Fresh Sweet Onions 3lb", "1", "produce", 164.81),
    ("2025-10-19", "Freshpet Dog Food Multi-Protein Recipe 3lb", "1", "pet", 164.81),
    ("2025-10-19", "Ghirardelli Milk Chocolate Baking Chips 11.5oz", "1", "baking", 164.81),
    ("2025-10-19", "Great Value Fruit Punch Drink Enhancer 3.11oz", "1", "drinks", 164.81),
    ("2025-10-19", "Great Value American Cheese Singles 16oz 24ct", "1", "dairy", 164.81),
    ("2025-10-19", "Great Value Mandarin & Teakwood Aromatherapy Candle 14oz", "1", "home", 164.81),
    ("2025-10-19", "Great Value Organic Ground White Pepper 2.05oz", "1", "spices", 164.81),
    ("2025-10-19", "Hungry Jack Hashbrown Potatoes 4.2oz", "1", "pantry", 164.81),
    ("2025-10-19", "Jimmy Dean Premium Pork Hot Sausage Roll 16oz", "2", "meat", 164.81),
    ("2025-10-19", "Jumbo Russet Potatoes 8lb", "1", "produce", 164.81),
    ("2025-10-19", "Marketside Caesar Salad with Chicken 12.1oz Tray", "1", "produce", 164.81),
    ("2025-10-19", "QuickSteak 100% Thin Sirloin Frozen Beef 10.8oz", "1", "frozen", 164.81),
    ("2025-10-19", "Rosarita Spicy Jalapeno Refried Beans 16oz", "1", "pantry", 164.81),
    ("2025-10-19", "Stove Top Stuffing Mix Chicken 6oz", "2", "pantry", 164.81),
    ("2025-10-19", "Tillamook Farmstyle Swiss Cheese Slices 8oz 9ct", "1", "dairy", 164.81),
    ("2025-10-19", "Tropicana Classic Lemonade 46oz", "2", "drinks", 164.81),
    ("2025-10-19", "Tropicana Strawberry Lemonade 46oz", "1", "drinks", 164.81),
    ("2025-10-19", "Tyson Oven Roasted Diced Chicken Breast 22oz Frozen", "1", "frozen", 164.81),

    # ─── OCT 25, 2025 — Store delivery $129.48 ──────────────────────────────
    ("2025-10-25", "3 Musketeers Fun Size Chocolate Candy Bars 10.48oz", "1", "snacks", 129.48),
    ("2025-10-25", "Crunch Pak Fresh Organic Peeled Sliced Apples 12oz", "1", "produce", 129.48),
    ("2025-10-25", "Darigold Whole Lactose Free Ultra Filtered Milk 59oz", "1", "dairy", 129.48),
    ("2025-10-25", "Florida Crystals Regenerative Organic Raw Cane Sugar 48oz", "2", "baking", 129.48),
    ("2025-10-25", "Franz Hawaiian Dinner Rolls 16oz 12ct", "1", "bread", 129.48),
    ("2025-10-25", "Fresh Romaine Lettuce", "1", "produce", 129.48),
    ("2025-10-25", "Freshness Guaranteed Yellow Cake Square w/ Chocolate Icing 6oz", "2", "bakery", 129.48),
    ("2025-10-25", "Giovanni Rana Ravioli Spinach Ricotta Family Size 18oz", "1", "frozen", 129.48),
    ("2025-10-25", "Great Value Seasoned Sirloin Beef Philly Steak 14oz", "1", "meat", 129.48),
    ("2025-10-25", "Kerrygold Naturally Softer Irish Butter 8oz Tub", "2", "dairy", 129.48),
    ("2025-10-25", "Lay's Classic Potato Snack Chips 1oz 10ct Multipack", "1", "snacks", 129.48),
    ("2025-10-25", "Litehouse Old Fashioned Caramel Dip Snack Size 6ct 2oz", "1", "snacks", 129.48),
    ("2025-10-25", "Marketside Caesar Bacon Chopped Salad Kit 10.2oz", "1", "produce", 129.48),
    ("2025-10-25", "Marketside Fresh Shredded Iceberg Lettuce 8oz", "1", "produce", 129.48),
    ("2025-10-25", "Marketside Ground Wagyu Beef 75/25 1lb", "2", "meat", 129.48),
    ("2025-10-25", "MiO Vitamins Orange Vanilla Water Enhancer 1.62oz", "2", "drinks", 129.48),
    ("2025-10-25", "Oikos Pro 20g Protein Vanilla Yogurt 5.3oz", "2", "dairy", 129.48),
    ("2025-10-25", "Tillamook Extra Creamy Unsalted Butter Sticks 4ct 16oz", "1", "dairy", 129.48),
    ("2025-10-25", "Utz Sourdough Specials Original Pretzels 26oz", "1", "snacks", 129.48),

    # ─── NOV 2/10, 2025 — Nearly all returned; only Olay kept ───────────────
    ("2025-11-10", "Olay Moisturizing Body Wash Spoonful of Sugar 22oz", "1", "health", 230.85),

    # ─── NOV 16, 2025 — Store + Online delivery $116.93 ─────────────────────
    ("2025-11-16", "Crest 3D White Toothpaste Radiant Mint 2.4oz", "1", "health", 116.93),
    ("2025-11-16", "Darigold Whole Milk Half Gallon 64oz", "1", "dairy", 116.93),
    ("2025-11-16", "Fresh Jalapeño Peppers ~0.5lb", "1", "produce", 116.93),
    ("2025-11-16", "Fresh Broccoli Crowns", "2", "produce", 116.93),
    ("2025-11-16", "Fresh Yellow Onions 3lb", "1", "produce", 116.93),
    ("2025-11-16", "Galbani Low Moisture Part Skim Mozzarella String Cheese 16oz 16ct", "1", "dairy", 116.93),
    ("2025-11-16", "Great Value Cream Cheese Brick 8oz", "1", "dairy", 116.93),
    ("2025-11-16", "Great Value Fresh Seal Double Zipper Sandwich Bags 100ct", "1", "household", 116.93),
    ("2025-11-16", "Great Value Sliced Black Olives 2.25oz", "1", "pantry", 116.93),
    ("2025-11-16", "Jif Extra Crunchy Peanut Butter 16oz", "1", "pantry", 116.93),
    ("2025-11-16", "Listerine Freshburst Antiseptic Mouthwash 1.5L", "1", "health", 116.93),
    ("2025-11-16", "Marketside Cinnamon Coffee Sliced Cake 3.5oz", "3", "bakery", 116.93),
    ("2025-11-16", "Marketside Fresh Shredded Iceberg Lettuce 8oz", "1", "produce", 116.93),
    ("2025-11-16", "MiO Vitamins Orange Vanilla Water Enhancer 1.62oz", "2", "drinks", 116.93),
    ("2025-11-16", "Prima Della Black Forest Ham Pre-Sliced", "1", "deli", 116.93),
    ("2025-11-16", "Reynolds Wrap Pre-Cut Pop-Up Aluminum Foil Sheets 50ct", "1", "household", 116.93),
    ("2025-11-16", "Scrubbing Bubbles Bathroom Grime Fighter Citrus 20oz 2-pack", "1", "cleaning", 116.93),
    ("2025-11-16", "Taylor Farms Caesar Salad with Bacon & Chicken 5.75oz", "1", "produce", 116.93),
    ("2025-11-16", "Tillamook Farmstyle Swiss Cheese Slices 8oz 9ct", "1", "dairy", 116.93),
    ("2025-11-18", "Fisher Chef's Naturals Gluten Free Almond Flour 16oz", "1", "baking", 116.93),

    # ─── NOV 30, 2025 — Store delivery $161.91 ──────────────────────────────
    ("2025-11-30", "Better Homes & Gardens Amber and Saffron Wooden Wick Candle 13oz", "1", "home", 161.91),
    ("2025-11-30", "Better Homes & Gardens Cashmere Teak Wooden Wick Candle 13oz", "1", "home", 161.91),
    ("2025-11-30", "Better Homes & Gardens Salted Coconut Mahogany 2-Wick Candle 12oz", "1", "home", 161.91),
    ("2025-11-30", "Downy Liquid Fabric Softener April Fresh 140oz 190 loads", "1", "laundry", 161.91),
    ("2025-11-30", "Equate Original 12-Hour Nasal Spray Max Strength 1oz", "3", "health", 161.91),
    ("2025-11-30", "Fresh Broccoli Crowns", "1", "produce", 161.91),
    ("2025-11-30", "Fresh Organic Granny Smith Apples 3lb", "1", "produce", 161.91),
    ("2025-11-30", "Fresh Pink Lady Apples 3lb", "1", "produce", 161.91),
    ("2025-11-30", "Freshpet Dog Food Multi-Protein Recipe 3lb", "1", "pet", 161.91),
    ("2025-11-30", "Honey Ohs! Family Size Cereal 20oz", "1", "cereal", 161.91),
    ("2025-11-30", "Kellogg's Frosted Krispies Breakfast Cereal Family Size 17.1oz", "1", "cereal", 161.91),
    ("2025-11-30", "Mainstays 3-Wick Scented Glass Jar Candle Creamy Cashmere 11.5oz", "1", "home", 161.91),
    ("2025-11-30", "Marketside Cinnamon Coffee Sliced Cake 3.5oz", "3", "bakery", 161.91),
    ("2025-11-30", "Marketside Fresh Shredded Iceberg Lettuce 8oz", "1", "produce", 161.91),
    ("2025-11-30", "MiO Vitamins Orange Vanilla Water Enhancer 1.62oz", "3", "drinks", 161.91),
    ("2025-11-30", "Great Value Heavy Whipping Cream 32oz", "2", "dairy", 161.91),
    ("2025-11-30", "Servio Grass Fed Non-GMO Traditional Ghee 10.58oz", "1", "dairy", 161.91),
    ("2025-11-30", "Stove Top Stuffing Mix Chicken 6oz", "1", "pantry", 161.91),
    ("2025-11-30", "Zatarain's Dirty Rice Dinner Mix 8oz", "1", "pantry", 161.91),

    # ─── DEC 5, 2025 — Subscription $29.97 ─────────────────────────────────
    ("2025-12-05", "Jocko Mölk Chocolate Protein Powder 21 Servings", "1", "health", 29.97),

    # ─── DEC 7, 2025 — Store + Online delivery $183.37 ──────────────────────
    ("2025-12-07", "Philadelphia Cream Cheese 8oz", "1", "dairy", 183.37),
    ("2025-12-07", "Wheat Chex Breakfast Cereal Family Size 19oz", "1", "cereal", 183.37),
    ("2025-12-07", "Better Homes & Gardens 5-Wick Ceramic Candle Red Lava & Citrus 40.5oz", "1", "home", 183.37),
    ("2025-12-07", "Corn Chex Gluten Free Breakfast Cereal Family Size 18oz", "1", "cereal", 183.37),
    ("2025-12-07", "Darigold Whole Milk Half Gallon 64oz", "1", "dairy", 183.37),
    ("2025-12-07", "Fresh Broccoli Crowns", "1", "produce", 183.37),
    ("2025-12-07", "Fresh Green Onions Bunch", "1", "produce", 183.37),
    ("2025-12-07", "Fresh Lemon", "1", "produce", 183.37),
    ("2025-12-07", "Freshness Guaranteed Sliced Italian Bread 14oz", "1", "bread", 183.37),
    ("2025-12-07", "Freshpet Dog Food Multi-Protein Recipe 3lb", "1", "pet", 183.37),
    ("2025-12-07", "Great Value Crisp and Salty Mini Pretzel Twists 16oz", "1", "snacks", 183.37),
    ("2025-12-07", "Marketside Fresh Shredded Iceberg Lettuce 8oz", "1", "produce", 183.37),
    ("2025-12-07", "MiO Vitamins Orange Vanilla Water Enhancer 1.62oz", "3", "drinks", 183.37),
    ("2025-12-07", "Nestle Toll House Butterscotch Baking Chips 11oz", "1", "baking", 183.37),
    ("2025-12-07", "Pork Belly Sliced Boneless ~1.5lb", "1", "meat", 183.37),
    ("2025-12-07", "Ratio Trio Yogurt Coconut 5.3oz", "1", "dairy", 183.37),
    ("2025-12-07", "Ratio Trio Yogurt Strawberry 5.3oz", "1", "dairy", 183.37),
    ("2025-12-07", "Ratio Trio Yogurt Vanilla 5.3oz", "2", "dairy", 183.37),
    ("2025-12-07", "Reese's Milk Chocolate Peanut Butter Trees 9.6oz", "2", "snacks", 183.37),
    ("2025-12-07", "Reese's Pieces Peanut Butter Candy 9oz", "1", "snacks", 183.37),
    ("2025-12-07", "Rice Chex Gluten Free Breakfast Cereal Family Size 18oz", "1", "cereal", 183.37),
    ("2025-12-07", "Stove Top Stuffing Mix Chicken 6oz", "1", "pantry", 183.37),
    ("2025-12-07", "Taylor Farms Caesar Salad with Bacon & Chicken 5.75oz", "1", "produce", 183.37),
    ("2025-12-15", "Nutricost Organic Coconut Flour 2lb", "1", "baking", 183.37),
    ("2025-12-15", "Nutricost Psyllium Whole Husk Powder 8oz", "1", "health", 183.37),

    # ─── DEC 19, 2025 — Store delivery $58.21 ───────────────────────────────
    ("2025-12-19", "Always Discreet Adult Incontinence Underwear XL 17ct", "1", "health", 58.21),
    ("2025-12-19", "Fresh Organic Zucchini Squash 2ct", "1", "produce", 58.21),
    ("2025-12-19", "Fresh Roma Tomato", "3", "produce", 58.21),
    ("2025-12-19", "Fresh Sliced Baby Bella Mushrooms 8oz", "1", "produce", 58.21),
    ("2025-12-19", "Miracle Noodle Angel Hair Konjac Noodles 7oz", "1", "pantry", 58.21),
    ("2025-12-19", "Miracle Noodle Spaghetti Konjac Noodles 7oz", "1", "pantry", 58.21),
    ("2025-12-19", "Pork Belly Sliced Boneless ~1.5lb", "1", "meat", 58.21),
    ("2025-12-19", "Tate's Bake Shop Walnut Chocolate Chip Cookies 7oz", "1", "snacks", 58.21),
    ("2025-12-19", "Time and Tru Women's Textured Stitch Sweater Green Vine XXXL", "1", "clothing", 58.21),

    # ─── DEC 26, 2025 — Subscription $26.97 ────────────────────────────────
    ("2025-12-26", "Jocko Mölk Chocolate Protein Powder 21 Servings", "1", "health", 26.97),

    # ─── DEC 27, 2025 — Store delivery $92.96 ───────────────────────────────
    ("2025-12-27", "Fresh Broccoli Crowns", "1", "produce", 92.96),
    ("2025-12-27", "Fresh Lemon", "2", "produce", 92.96),
    ("2025-12-27", "Fresh Lime", "1", "produce", 92.96),
    ("2025-12-27", "Fresh Zucchini", "2", "produce", 92.96),
    ("2025-12-27", "Fresh Roma Tomato", "3", "produce", 92.96),
    ("2025-12-27", "Fresh Yellow Squash", "1", "produce", 92.96),
    ("2025-12-27", "Freshness Guaranteed Sliced White Mushrooms 8oz", "1", "produce", 92.96),
    ("2025-12-27", "Freshpet Dog Food Multi-Protein Recipe 3lb", "1", "pet", 92.96),
    ("2025-12-27", "Guerrero Zero Net Carbs Original Tortillas Street Taco 14ct", "1", "bread", 92.96),
    ("2025-12-27", "MiO Vitamins Orange Vanilla Water Enhancer 1.62oz", "2", "drinks", 92.96),
    ("2025-12-27", "Miracle Noodle Spaghetti Konjac Noodles 7oz", "1", "pantry", 92.96),
    ("2025-12-27", "Mission Zero Net Carbs Flour Tortillas 8ct", "1", "bread", 92.96),
    ("2025-12-27", "Ocean's Halo Organic Ramen Noodles 8.4oz", "1", "pantry", 92.96),
    ("2025-12-27", "Prima Della Black Forest Ham Pre-Sliced", "1", "deli", 92.96),
    ("2025-12-27", "Ratio Trio Yogurt Coconut 5.3oz", "1", "dairy", 92.96),
    ("2025-12-27", "Ratio Trio Yogurt Strawberry 5.3oz", "1", "dairy", 92.96),
    ("2025-12-27", "Ratio Trio Yogurt Vanilla 5.3oz", "4", "dairy", 92.96),
    ("2025-12-27", "Scent Theory Foaming Hand Soap Coconut & Ocean Mist 11oz", "2", "household", 92.96),
    ("2025-12-27", "Stove Top Stuffing Mix Chicken 6oz", "1", "pantry", 92.96),
    ("2025-12-27", "Tillamook Colby Jack Cheese Block 16oz", "1", "dairy", 92.96),
    ("2025-12-27", "Tillamook Pepper Jack Cheese Block 8oz", "2", "dairy", 92.96),

    # ─── JAN 3, 2026 — Store delivery $120.35 ───────────────────────────────
    ("2026-01-03", "Applegate Naturals Black Forest Uncured Ham 7oz", "1", "deli", 120.35),
    ("2026-01-03", "Ben's Original Butter & Garlic Ready Rice 8.8oz", "1", "pantry", 120.35),
    ("2026-01-03", "Ben's Original Ready Rice Pilaf 8.8oz", "1", "pantry", 120.35),
    ("2026-01-03", "Ben's Original Ready Rice Spanish Style 8.8oz", "1", "pantry", 120.35),
    ("2026-01-03", "Darigold Whole Milk Half Gallon 64oz", "1", "dairy", 120.35),
    ("2026-01-03", "Fresh Broccoli Crowns", "1", "produce", 120.35),
    ("2026-01-03", "Fresh Roma Tomato", "2", "produce", 120.35),
    ("2026-01-03", "Fresh Sliced Baby Bella Mushrooms 8oz", "1", "produce", 120.35),
    ("2026-01-03", "Fresh Sweet Onions 3lb", "1", "produce", 120.35),
    ("2026-01-03", "Freshpet Dog Food Multi-Protein Recipe 3lb", "1", "pet", 120.35),
    ("2026-01-03", "Galbani Low Moisture Part Skim Mozzarella String Cheese 16oz 16ct", "1", "dairy", 120.35),
    ("2026-01-03", "Great Value Hot Mexican-Style Chili Powder 2.5oz", "1", "spices", 120.35),
    ("2026-01-03", "Great Value Organic Chili Powder 2oz", "1", "spices", 120.35),
    ("2026-01-03", "Great Value Organic Smoked Paprika 1.6oz", "1", "spices", 120.35),
    ("2026-01-03", "Great Value Thyme Leaves 0.75oz", "1", "spices", 120.35),
    ("2026-01-03", "Honey Nut Cheerios Mega Size 27.2oz", "1", "cereal", 120.35),
    ("2026-01-03", "Lea & Perrins Worcestershire Sauce 10oz", "1", "condiments", 120.35),
    ("2026-01-03", "Marketside Fresh Shredded Iceberg Lettuce 8oz", "1", "produce", 120.35),
    ("2026-01-03", "MiO Vitamins Orange Vanilla Water Enhancer 1.62oz", "2", "drinks", 120.35),
    ("2026-01-03", "Q Fried Pork Skins 4oz", "2", "snacks", 120.35),
    ("2026-01-03", "Quality Bell Pepper Strips Frozen 14oz", "2", "frozen", 120.35),
    ("2026-01-03", "Ratio Trio Yogurt Vanilla 5.3oz", "4", "dairy", 120.35),
    ("2026-01-03", "Super Poligrip Extra Strength Denture Adhesive Powder 1.6oz", "1", "health", 120.35),
    ("2026-01-03", "Wilcox Farms Free-Range Eggs 6ct Individually Wrapped", "2", "dairy", 120.35),

    # ─── JAN 11, 2026 — Partial cancel — only 2 items delivered ─────────────
    ("2026-01-11", "Mainstays 3-Wick Ombre Wrap Garden Rain Candle 14oz", "1", "home", 13.04),
    ("2026-01-11", "Mizkan Rice Vinegar for Cooking 12oz", "1", "condiments", 13.04),

    # ─── JAN 12, 2026 — Store delivery $113.45 ──────────────────────────────
    ("2026-01-12", "BelGioioso Blue Cheese Freshly Crumbled Cup 5oz", "1", "dairy", 113.45),
    ("2026-01-12", "Chuck Roast Choice Angus Beef Family Pack 3.25-4.25lb", "1", "meat", 113.45),
    ("2026-01-12", "Fresh Broccoli Crowns", "2", "produce", 113.45),
    ("2026-01-12", "Fresh Zucchini", "3", "produce", 113.45),
    ("2026-01-12", "Fresh Sliced Baby Bella Mushrooms 8oz", "1", "produce", 113.45),
    ("2026-01-12", "Fresh Strawberries 1lb", "1", "produce", 113.45),
    ("2026-01-12", "Fresh Yellow Squash", "2", "produce", 113.45),
    ("2026-01-12", "Mainstays 3-Wick Wrapped Clouds & Rainbows Scented Candle 14oz", "1", "home", 113.45),
    ("2026-01-12", "Marketside Fresh Baby Spinach 11oz", "1", "produce", 113.45),
    ("2026-01-12", "Oscar Mayer Deli Fresh Honey Uncured Ham 9oz", "2", "deli", 113.45),
    ("2026-01-12", "Q Fried Pork Skins 4oz", "3", "snacks", 113.45),
    ("2026-01-12", "San J Tamari Soy Sauce Organic 10oz", "1", "condiments", 113.45),

    # ─── JAN 16, 2026 — Subscription $26.97 ────────────────────────────────
    ("2026-01-16", "Jocko Mölk Chocolate Protein Powder 21 Servings", "1", "health", 26.97),

    # ─── JAN 27, 2026 — Store delivery $54.83 ───────────────────────────────
    ("2026-01-27", "Cascade Platinum Dishwasher Pods Fresh 12ct", "1", "household", 54.83),
    ("2026-01-27", "Assurance Women's Incontinence Underwear XL Max Absorbency 19ct", "1", "health", 54.83),
    ("2026-01-27", "Jumbo Russet Potatoes 8lb", "1", "produce", 54.83),
    ("2026-01-27", "Great Value Fruit Punch Drink Enhancer 3.11oz", "1", "drinks", 54.83),
    ("2026-01-27", "Marketside Fresh Shredded Iceberg Lettuce 8oz", "1", "produce", 54.83),
    ("2026-01-27", "MiO Vitamins Orange Vanilla Water Enhancer 1.62oz", "2", "drinks", 54.83),
    ("2026-01-27", "Milo's 100% Natural Famous Unsweet Iced Tea 128oz", "1", "drinks", 54.83),
    ("2026-01-27", "Lindt Excellence Dark Chocolate 90% Cocoa 3.5oz", "2", "snacks", 54.83),
    ("2026-01-27", "Fresh Sliced Baby Bella Mushrooms 8oz", "1", "produce", 54.83),

    # ─── FEB 1/2, 2026 — Online $15.38 ─────────────────────────────────────
    ("2026-02-02", "Tim Hortons Decaf Ground Coffee 12oz Bag", "2", "pantry", 15.38),

    # ─── FEB 2, 2026 — In-store $38.85 ─────────────────────────────────────
    ("2026-02-02", "Blink Contacts Rewetting & Lubricant Eye Drops 0.34oz", "1", "health", 38.85),
    ("2026-02-02", "Biotrue Multi-Purpose Contact Lens Solution & Case 10oz", "1", "health", 38.85),
    ("2026-02-02", "Equate Contact Lens Cases 6ct", "1", "health", 38.85),
    ("2026-02-02", "Equate Interdental Brushes w/ Antibacterial Caps Mint Tight 20ct", "1", "health", 38.85),
    ("2026-02-02", "TheraBreath Healthy Gums Mouthwash Clean Mint 16oz", "1", "health", 38.85),

    # ─── FEB 6/8, 2026 — Subscription $26.97 ───────────────────────────────
    ("2026-02-08", "Jocko Mölk Chocolate Protein Powder 21 Servings", "1", "health", 26.97),

    # ─── FEB 12, 2026 — In-store $46.77 ────────────────────────────────────
    ("2026-02-12", "Assurance Women's Incontinence Underwear XL Max Absorbency 36ct", "1", "health", 46.77),
    ("2026-02-12", "Equate Original 12-Hour Nasal Spray Max Strength 1oz", "2", "health", 46.77),
    ("2026-02-12", "Germ-X Advanced Hand Sanitizer with Aloe 12oz", "1", "health", 46.77),
    ("2026-02-12", "Liquid I.V. White Peach Sugar-Free Hydration Multiplier 6ct", "1", "health", 46.77),
    ("2026-02-12", "Reese's Milk Chocolate Peanut Butter Eggs Easter 9.6oz", "1", "snacks", 46.77),
    ("2026-02-12", "American Greetings Gift Bows Assorted", "3", "household", 46.77),

    # ─── FEB 15, 2026 — Online delivery $221.94 ─────────────────────────────
    ("2026-02-15", "Fresh Broccoli Crowns", "1", "produce", 221.94),
    ("2026-02-15", "Fresh Sliced Baby Bella Mushrooms 8oz", "1", "produce", 221.94),
    ("2026-02-15", "Great Day Farms Hard-Boiled Cage Free Eggs 6ct", "2", "dairy", 221.94),
    ("2026-02-15", "Great Value American Cheese Singles 16oz 24ct", "1", "dairy", 221.94),
    ("2026-02-15", "Franz Cracked Wheat Bread Loaf 22.5oz", "1", "bread", 221.94),
    ("2026-02-15", "Great Value Hamburger Buns 11oz 8ct", "1", "bread", 221.94),
    ("2026-02-15", "Kerrygold Grass-Fed Pure Irish Butter 8oz Tub", "2", "dairy", 221.94),
    ("2026-02-15", "Great Value Heavy Whipping Cream 32oz", "1", "dairy", 221.94),
    ("2026-02-15", "Freshpet Dog Food Homestyle Creations Chicken & Turkey 1lb", "1", "pet", 221.94),
    ("2026-02-15", "Freshpet Dog Food Small Dog Beef & Egg Recipe 1lb", "1", "pet", 221.94),
    ("2026-02-15", "Freshpet Dog Food Multi-Protein Recipe 3lb", "1", "pet", 221.94),
    ("2026-02-15", "Johnsonville Hot Italian Pork Sausage Links 19oz 5ct", "2", "meat", 221.94),
    ("2026-02-15", "Tyson Southern Style Chicken Breast Tenderloins 25oz", "1", "frozen", 221.94),
    ("2026-02-15", "Yellowstone BBQ Meatloaf & Mashed Potatoes 13.5oz", "2", "frozen", 221.94),
    ("2026-02-15", "Bob Evans Gluten-Free Original Mashed Potatoes 12oz 2ct", "2", "frozen", 221.94),
    ("2026-02-15", "Prego Traditional Pasta Sauce 24oz", "1", "pantry", 221.94),
    ("2026-02-15", "Manwich Original Sloppy Joe Sauce 15oz", "1", "pantry", 221.94),
    ("2026-02-15", "Morton Iodized Salt 26oz", "1", "spices", 221.94),
    ("2026-02-15", "Lay's Potato Chips Bacon Grilled Cheese 7.75oz", "1", "snacks", 221.94),
    ("2026-02-15", "Ratio Trio Yogurt Vanilla Keto 5.3oz", "4", "dairy", 221.94),
    ("2026-02-15", "Ratio Trio Yogurt Coconut Keto 5.3oz", "1", "dairy", 221.94),
    ("2026-02-15", "Ratio Yogurt Protein Strawberry 5.3oz", "1", "dairy", 221.94),
    ("2026-02-15", "Reese's Pieces Peanut Butter Candy 9oz", "1", "snacks", 221.94),
    ("2026-02-15", "20 Mule Team All Natural Borax 65oz", "1", "cleaning", 221.94),
    ("2026-02-15", "Cascade Platinum Plus Dishwasher Pods Fresh 47ct", "1", "household", 221.94),
    ("2026-02-15", "Lakanto Original Liquid Monk Fruit Extract Drops 1.76oz", "1", "baking", 221.94),
    ("2026-02-15", "Better Homes & Gardens Lavender & Lemonade 2-Wick Candle 18oz", "1", "home", 221.94),
    ("2026-02-15", "Mainstays 3-Wick Raspberry Peach Candle 14oz", "1", "home", 221.94),
    ("2026-02-15", "Mainstays 3-Wick Glass Jar Candle Beachside Linen 11.5oz", "1", "home", 221.94),
    ("2026-02-15", "Mainstays 3-Wick Cranberry Mandarin Candle 14oz", "1", "home", 221.94),

    # ─── FEB 17, 2026 — In-store $2.94 ──────────────────────────────────────
    ("2026-02-17", "Great Value Hot Premium Sausage Roll 16oz", "1", "meat", 2.94),

    # ─── FEB 18, 2026 — In-store $74.92 ─────────────────────────────────────
    ("2026-02-18", "Ben & Jerry's Americone Dream Ice Cream Pint 16oz", "1", "frozen", 74.92),
    ("2026-02-18", "Great Value Butter Pecan Ice Cream 16oz", "2", "frozen", 74.92),
    ("2026-02-18", "Mountain Dew Citrus Soda Pop Mini Cans 7.5oz 6-pack", "1", "drinks", 74.92),
    ("2026-02-18", "RC Cola Soda Pop 12oz 12-pack", "1", "drinks", 74.92),
    ("2026-02-18", "Great Value Distilled Water 1 Gallon", "1", "drinks", 74.92),
    ("2026-02-18", "Great Value Orange Blast Water Drink Enhancer 3.11oz", "1", "drinks", 74.92),
    ("2026-02-18", "M&M's Peanut Chocolate Candy Share Size 3.27oz", "1", "snacks", 74.92),
    ("2026-02-18", "NeilMed Sinus Rinse Kit 50 packets", "1", "health", 74.92),
    ("2026-02-18", "Afrin No Drip Extra Moisturizing Nasal Spray 15mL", "1", "health", 74.92),
    ("2026-02-18", "No Drip Nasal Spray Oxymetazoline HCl 1oz", "1", "health", 74.92),
    ("2026-02-18", "Band-Aid Small Cushion Care Thick Gauze Pads 2x2in 25ct", "1", "health", 74.92),
    ("2026-02-18", "Equate Gentle Paper Tape White 2ct", "1", "health", 74.92),

    # ─── FEB 21, 2026 — Online delivery $225.42 (returns excluded) ──────────
    ("2026-02-21", "Freshpet Dog Food Homestyle Creations Beef/Chicken/Turkey 1lb", "1", "pet", 225.42),
    ("2026-02-21", "Freshpet Dog Food Multi-Protein Recipe 3lb", "1", "pet", 225.42),
    ("2026-02-21", "Kerrygold Grass-Fed Pure Irish Butter 8oz Tub", "3", "dairy", 225.42),
    ("2026-02-21", "Tillamook Pepper Jack Cheese Block 8oz", "1", "dairy", 225.42),
    ("2026-02-21", "Tillamook Colby Jack Cheese Block 16oz", "1", "dairy", 225.42),
    ("2026-02-21", "Bar-S Thick Bologna Deli-Style 1lb", "1", "deli", 225.42),
    ("2026-02-21", "Yellowstone BBQ Meatloaf & Mashed Potatoes 13.5oz", "2", "frozen", 225.42),
    ("2026-02-21", "Ore-Ida Classic Thick Cut Steak Fries 28oz", "1", "frozen", 225.42),
    ("2026-02-21", "Bob Evans Gluten-Free Original Mashed Potatoes 12oz 2ct", "1", "frozen", 225.42),
    ("2026-02-21", "Del Monte Golden Sweet Whole Kernel Corn 15.25oz", "2", "pantry", 225.42),
    ("2026-02-21", "Del Monte Golden Sweet Cream Corn 14.75oz", "1", "pantry", 225.42),
    ("2026-02-21", "Stove Top Stuffing Mix Chicken 6oz", "1", "pantry", 225.42),
    ("2026-02-21", "Ocean's Halo Organic Ramen Noodles 8.4oz", "1", "pantry", 225.42),
    ("2026-02-21", "Ghirardelli Caramel Walnut Premium Brownie Mix 18.5oz", "1", "baking", 225.42),
    ("2026-02-21", "RITZ Fresh Stacks Original Crackers Family Size 17.8oz", "1", "snacks", 225.42),
    ("2026-02-21", "Mountain Dew Citrus Soda Pop Mini Cans 7.5oz 10-pack", "1", "drinks", 225.42),
    ("2026-02-21", "RC Cola Soda Pop 12oz 24-pack", "1", "drinks", 225.42),
    ("2026-02-21", "Parent's Choice Distilled Water 1 Gallon", "1", "drinks", 225.42),
    ("2026-02-21", "MiO Orange Tangerine Sugar Free Water Enhancer 3.24oz", "2", "drinks", 225.42),
    ("2026-02-21", "MiO Vitamins Orange Vanilla Water Enhancer 1.62oz", "2", "drinks", 225.42),
    ("2026-02-21", "Reese's Pieces Peanut Butter Candy 9oz", "1", "snacks", 225.42),
    ("2026-02-21", "M&M's Peanut Chocolate Candy Share Size 3.27oz", "1", "snacks", 225.42),
    ("2026-02-21", "Great Value Lemon Scent Disinfecting Wipes 75ct", "1", "cleaning", 225.42),
    ("2026-02-21", "Sterilite Clear Pitcher 1 Gallon", "1", "household", 225.42),
    ("2026-02-21", "Sky Valley Sambal Oelek Chili Paste 7oz", "1", "condiments", 225.42),

    # ─── FEB 21 separate orders ──────────────────────────────────────────────
    ("2026-02-21", "Fixodent Ultra Max Hold Secure Denture Adhesive Cream 2.2oz", "1", "health", 7.07),
    ("2026-02-21", "Scent Theory Foaming Hand Soap Coconut & Ocean Mist 11oz", "2", "household", 6.42),
]


def seed():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")

    # Create table if needed (mirrors db.py init_db)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS purchase_history (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            purchased_at TEXT NOT NULL,
            name         TEXT NOT NULL,
            quantity     TEXT DEFAULT '1',
            category     TEXT DEFAULT '',
            order_total  REAL,
            source       TEXT DEFAULT 'walmart'
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ph_name ON purchase_history(name COLLATE NOCASE)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ph_date ON purchase_history(purchased_at)")

    existing = conn.execute("SELECT COUNT(*) FROM purchase_history").fetchone()[0]
    if existing > 0:
        print(f"purchase_history already has {existing} rows. Skipping seed to avoid duplicates.")
        print("To re-seed, run: DELETE FROM purchase_history; then re-run this script.")
        conn.close()
        return

    conn.executemany(
        "INSERT INTO purchase_history (purchased_at, name, quantity, category, order_total, source) VALUES (?, ?, ?, ?, ?, 'walmart')",
        HISTORY,
    )
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM purchase_history").fetchone()[0]
    conn.close()
    print(f"Seeded {count} purchase history rows.")


if __name__ == "__main__":
    seed()
