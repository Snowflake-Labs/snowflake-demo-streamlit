-- Database and Schema creation
CREATE DATABASE SampleDatabase;
USE DATABASE SampleDatabase;
CREATE SCHEMA InventoryTracker;
USE SCHEMA InventoryTracker;

CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT,
    price REAL,
    units_sold INTEGER,
    units_left INTEGER,
    cost_price REAL,
    reorder_point INTEGER,
    description TEXT,
    image TEXT
);

INSERT INTO
    inventory (
        item_name,
        price,
        units_sold,
        units_left,
        cost_price,
        reorder_point,
        description,
        image
    )
VALUES
    (
        'Milk',
        2.99,
        200,
        50,
        1.50,
        20,
        'Fresh dairy product rich in calcium',
        'https://www.heritagefoods.in/blog/wp-content/uploads/2020/12/shutterstock_539045662.jpg'
    ),
    (
        'Bread',
        1.99,
        300,
        80,
        1.20,
        30,
        'Staple food item made from flour',
        'https://www.allrecipes.com/thmb/CjzJwg2pACUzGODdxJL1BJDRx9Y=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/6788-amish-white-bread-DDMFS-4x3-6faa1e552bdb4f6eabdd7791e59b3c84.jpg'
    ),
    (
        'Eggs',
        2.49,
        400,
        100,
        1.80,
        40,
        'Protein-rich food item used in various recipes',
        'https://cdn.britannica.com/94/151894-050-F72A5317/Brown-eggs.jpg'
    ),
    (
        'Bananas',
        0.49,
        500,
        120,
        0.30,
        50,
        'Nutrient-rich fruit with potassium',
        'https://images.everydayhealth.com/images/diet-nutrition/all-about-bananas-nutrition-facts-health-benefits-recipes-and-more-rm-722x406.jpg'
    ),
    (
        'Cereal',
        3.99,
        250,
        70,
        2.50,
        25,
        'Breakfast food made from grains',
        'https://images-prod.healthline.com/hlcmsresource/images/AN_images/are-breakfast-cereals-healthy-1296x728-feature.jpg'
    ),
    (
        'Tomatoes',
        1.29,
        350,
        90,
        0.80,
        35,
        'Versatile vegetable used in salads, sauces',
        'https://media.post.rvohealth.io/wp-content/uploads/2020/09/AN313-Tomatoes-732x549-Thumb.jpg'
    ),
    (
        'Chicken Breast',
        5.99,
        150,
        30,
        4.00,
        15,
        'Lean protein source suitable for grilling',
        'https://www.southernliving.com/thmb/-TWfCwlFHd-7DIzTIYXh2Zxr_f8=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/How_To_Grill_Chicken_010-e4aff40705b247868fe3fb6755e8bdd4.jpg'
    ),
    (
        'Rice',
        2.79,
        450,
        100,
        1.50,
        40,
        'Staple grain used as a side dish',
        'https://www.onceuponachef.com/images/2014/10/jasmine-rice-1.jpg'
    ),
    (
        'Pasta',
        1.79,
        400,
        80,
        1.00,
        30,
        'Versatile carbohydrate source',
        'https://assets.epicurious.com/photos/5988e3458e3ab375fe3c0caf/1:1/w_3607,h_3607,c_limit/How-to-Make-Chicken-Alfredo-Pasta-hero-02082017.jpg'
    ),
    (
        'Potatoes',
        0.99,
        300,
        50,
        0.60,
        25,
        'Versatile vegetable used in soups, salads',
        'https://cdn.mos.cms.futurecdn.net/iC7HBvohbJqExqvbKcV3pP-1200-80.jpg'
    ),
    (
        'Spinach',
        1.89,
        200,
        40,
        1.20,
        20,
        'Nutrient-rich leafy green vegetable',
        'https://cdn.britannica.com/30/82530-050-79911DD4/Spinach-leaves-vitamins-source-person.jpg'
    ),
    (
        'Apples',
        1.49,
        350,
        60,
        0.90,
        30,
        'Crisp and sweet fruit packed with fiber',
        'https://www.foodandwine.com/thmb/h7XBIk5uparmVpDEyQ9oC7brCpA=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/A-Feast-of-Apples-FT-2-MAG1123-980271d42b1a489bab239b1466588ca4.jpg'
    ),
    (
        'Carrots',
        0.79,
        400,
        70,
        0.50,
        35,
        'Crunchy vegetable rich in beta-carotene',
        'https://ucarecdn.com/459eb7be-115a-4d85-b1d8-deaabc94c643/-/format/auto/-/preview/3000x3000/-/quality/lighter/'
    ),
    (
        'Ground Beef',
        6.49,
        200,
        30,
        5.00,
        20,
        'Versatile meat used in various recipes',
        'https://www.allrecipes.com/thmb/tQq1D3TigZEeysde4qL0LZ0N9D4=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/229112-ground-beef-with-homemade-taco-seasoning-mix-DDMFS-4x3-719013d51e844a948c0b39cccb5ed908.jpg'
    ),
    (
        'Yogurt',
        2.29,
        300,
        50,
        1.50,
        25,
        'Dairy product containing live cultures',
        'https://www.eatingwell.com/thmb/3D5Biw_HmvJ3f4-EnAGq3DINUzk=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/3758635-8f162783cbf84ec385e122727ecbe396.jpg'
    ),
    (
        'Cheese',
        3.49,
        250,
        40,
        2.00,
        20,
        'Dairy product with various flavors and textures',
        'https://images-prod.healthline.com/hlcmsresource/images/AN_images/healthiest-cheese-1296x728-swiss.jpg'
    ),
    (
        'Onions',
        0.89,
        400,
        60,
        0.60,
        30,
        'Aromatic vegetable used as a base ingredient',
        'https://cdn-prod.medicalnewstoday.com/content/images/articles/276/276714/red-and-white-onions.jpg'
    ),
    (
        'Salmon Fillet',
        9.99,
        100,
        10,
        7.00,
        5,
        'Fatty fish rich in omega-3 fatty acids',
        'https://altonbrown.com/wp-content/uploads/2020/08/IMG_3444-scaled.jpeg'
    ),
    (
        'Orange Juice',
        2.99,
        300,
        40,
        1.80,
        30,
        'Refreshing beverage rich in vitamin C',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Orangejuice.jpg/1200px-Orangejuice.jpg'
    ),
    (
        'Frozen Pizza',
        4.49,
        150,
        20,
        3.00,
        15,
        'Convenient meal option',
        'https://www.allrecipes.com/thmb/aefJMDXKqs42oAP71dQuYf_-Qdc=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/6776_Pizza-Dough_ddmfs_4x3_1724-fd91f26e0bd6400a9e89c6866336532b.jpg'
    ),
    (
        'Cucumber',
        0.69,
        400,
        50,
        0.40,
        30,
        'Crisp vegetable often used in salads',
        'https://sa1s3optim.patientpop.com/assets/images/provider/photos/2445929.png'
    ),
    (
        'Broccoli',
        1.99,
        250,
        30,
        1.20,
        20,
        'Nutrient-rich vegetable high in fiber',
        'https://i0.wp.com/images-prod.healthline.com/hlcmsresource/images/AN_images/health-benefits-of-broccoli-1296x728-feature.jpg?w=1155&h=1528'
    ),
    (
        'Turkey',
        4.99,
        200,
        20,
        3.00,
        15,
        'Lean protein source used as a healthier alternative',
        'https://www.allrecipes.com/thmb/cVQL59QQ70ikOvtpcZU3TmQRPkg=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/ALR-166160-juicy-thanksgiving-turkey-VAT-4958-4x3-e9fdc719770d4661b5d831f958e6eb78.jpg'
    ),
    (
        'Olive Oil',
        7.99,
        100,
        10,
        5.00,
        5,
        'Healthy cooking oil',
        'https://www.womansworld.com/wp-content/uploads/2021/02/oil.jpg?w=953'
    ),
    (
        'Bacon',
        4.99,
        150,
        20,
        3.50,
        15,
        'Savory cured meat used as a breakfast item',
        'https://images.immediate.co.uk/production/volatile/sites/30/2019/11/Bacon-rashers-in-a-pan-72c07f4.jpg?quality=90&resize=556,505'
    ),
    (
        'Avocado',
        1.99,
        300,
        30,
        1.20,
        25,
        'Creamy fruit rich in healthy fats',
        'https://t3.ftcdn.net/jpg/05/98/40/14/360_F_598401408_PbB7tyKvnfXLdyIhcKFd3rWhc0XJrD18.jpg'
    ),
    (
        'Strawberries',
        3.99,
        200,
        20,
        2.50,
        15,
        'Sweet and juicy berries',
        'https://www.allrecipes.com/thmb/1c99SWam7_FM6vUzpDDzIKffMR4=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/ALR-strawberry-fruit-or-vegetable-f6dd901427714e46af2d706a57b9016f.jpg'
    ),
    (
        'Lettuce',
        1.29,
        350,
        40,
        0.80,
        30,
        'Crisp and refreshing leafy green vegetable',
        'https://www.bhg.com/thmb/oL0DwR0DXrhFynA2y-oiY-nkCbg=/1878x0/filters:no_upscale():strip_icc()/tango-oakleaf-lettuce-c6f6417e-4cffa63034624d96a9e9ec9a3fe158f9.jpg'
    ),
    (
        'Green Beans',
        1.79,
        250,
        30,
        1.00,
        20,
        'Nutrient-rich vegetable often served as a side dish',
        'https://www.allrecipes.com/thmb/8pUciYflYqcGvFgOjPARnAWi7NU=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/230103-buttery-garlic-green-beans-DDMFS-4x3-43cfc64c1dae47d5897f7bee21f21cda.jpg'
    ),
    (
        'Pork',
        5.49,
        200,
        20,
        4.00,
        15,
        'Versatile meat used in various recipes',
        'https://www.comedera.com/wp-content/uploads/2023/09/shutterstock_2175078831.jpg'
    ),
    (
        'Almonds',
        6.99,
        100,
        10,
        4.50,
        5,
        'Nutrient-dense nuts rich in healthy fats',
        'https://images.immediate.co.uk/production/volatile/sites/30/2021/02/almonds-9e25ce7.jpg?quality=90&resize=556,505'
    ),
    (
        'White Bread',
        1.49,
        400,
        40,
        0.90,
        35,
        'Soft and fluffy bread',
        'https://www.jocooks.com/wp-content/uploads/2020/03/white-bread-1-500x375.jpg'
    ),
    (
        'Cabbage',
        0.79,
        300,
        30,
        0.50,
        25,
        'Crunchy vegetable used in coleslaw',
        'https://snaped.fns.usda.gov/sites/default/files/styles/crop_ratio_7_5/public/seasonal-produce/2018-05/cabbage.jpg?h=ea25e381&itok=X5fHv9z-'
    ),
    (
        'Tuna',
        2.99,
        200,
        20,
        2.00,
        15,
        'Lean protein source',
        'https://www.lecremedelacrumb.com/wp-content/uploads/2022/03/tuna-steaks-marinade-1-2.jpg'
    ),
    (
        'Lemons',
        0.99,
        350,
        30,
        0.60,
        25,
        'Citrus fruit known for its tart flavor',
        'https://loveincstatic.blob.core.windows.net/lovefood/2020/Guide-to-lemons/history-of-lemons.jpg'
    ),
    (
        'Ground Chicken',
        4.49,
        150,
        15,
        3.00,
        10,
        'Lean protein option',
        'https://recipes.net/wp-content/uploads/2023/10/how-to-cook-ground-chicken-in-a-pan-1698477574.jpg'
    ),
    (
        'Black Beans',
        1.29,
        300,
        30,
        0.80,
        25,
        'Protein and fiber-rich legume',
        'https://cdn.loveandlemons.com/wp-content/uploads/2021/02/black-bean-recipes.jpg'
    ),
    (
        'Peanut Butter',
        3.99,
        200,
        20,
        2.50,
        15,
        'Spread made from ground peanuts',
        'https://hips.hearstapps.com/hmg-prod/images/peanut-butter-vegan-1556206811.jpg?crop=0.8888888888888888xw:1xh;center,top&resize=1200:*'
    ),
    (
        'Bell Peppers',
        1.49,
        350,
        30,
        0.90,
        25,
        'Colorful and crunchy vegetables',
        'https://snaped.fns.usda.gov/sites/default/files/styles/crop_ratio_7_5/public/seasonal-produce/2018-05/bell%20peppers.jpg?h=9f30bee3&itok=4RHaus1z'
    ),
    (
        'Grapes',
        4.99,
        30,
        20,
        2.49,
        15,
        'Purple fruit',
        'https://www.thespruceeats.com/thmb/l1_lV7wgpqRArWBwpG3jzHih_e8=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/what-are-grapes-5193263-hero-01-80564d77b6534aa8bfc34f378556e513.jpg'
    ),
    (
        'Soy Milk',
        3.49,
        200,
        25,
        5.99,
        15,
        'Dairy-free alternative to cow milk',
        'https://assets.epicurious.com/photos/5fd9170f12a4c40b57e70f4b/1:1/w_2950,h_2950,c_limit/SoyMilk_RECIPE_IG_121020_6321_VOG_test.jpg'
    );