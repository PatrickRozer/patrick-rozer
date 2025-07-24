
SELECT "City", COUNT(*) AS provider_count
FROM public."Providers_db"
GROUP BY "City"
ORDER BY provider_count DESC;

SELECT "City", COUNT(*) AS receiver_count
FROM public."Receiver_db"
GROUP BY "City"
ORDER BY receiver_count DESC;

SELECT "Provider_Type", SUM("Quantity") AS total_food_quantity
FROM public."Food_Listing_db"
GROUP BY "Provider_Type"
ORDER BY total_food_quantity DESC
LIMIT 1;


SELECT "Name", "Contact"
FROM public."Providers_db"
WHERE "City" = 'YourCityName';


SELECT r."Name", r."Contact", SUM(f."Quantity") AS total_claimed_quantity
FROM public."Claim_db" c
JOIN public."Receiver_db" r ON c."Receiver_ID" = r."Receiver_ID"
JOIN public."Food_Listing_db" f ON c."Food_ID" = f."Food_ID"
WHERE c."Status" = 'Completed'
GROUP BY r."Receiver_ID", r."Name", r."Contact"
ORDER BY total_claimed_quantity DESC
LIMIT 10;


SELECT SUM("Quantity") AS total_available_food
FROM public."Food_Listing_db"
WHERE "Expiry_Date" >= CURRENT_DATE;


SELECT "Location" AS city, COUNT(*) AS food_listing_count
FROM public."Food_Listing_db"
GROUP BY "Location"
ORDER BY food_listing_count DESC
LIMIT 1;

SELECT "Food_Type", COUNT(*) AS count_food_type
FROM public."Food_Listing_db"
GROUP BY "Food_Type"
ORDER BY count_food_type DESC;


SELECT f."Food_Name", COUNT(c."Claim_ID") AS claim_count
FROM public."Claim_db" c
JOIN public."Food_Listing_db" f ON c."Food_ID" = f."Food_ID"
GROUP BY f."Food_ID", f."Food_Name"
ORDER BY claim_count DESC;

SELECT p."Name", COUNT(c."Claim_ID") AS successful_claims
FROM public."Claim_db" c
JOIN public."Food_Listing_db" f ON c."Food_ID" = f."Food_ID"
JOIN public."Providers_db" p ON f."Provider_ID" = p."Provider_ID"
WHERE c."Status" = 'Completed'
GROUP BY p."Provider_ID", p."Name"
ORDER BY successful_claims DESC
LIMIT 1;

SELECT "Status", 
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM public."Claim_db"), 2) AS percent
FROM public."Claim_db" 
GROUP BY "Status";

SELECT r."Name", AVG(f."Quantity") AS avg_food_quantity_claimed
FROM public."Claim_db"  c
JOIN public."Receiver_db" r ON c."Receiver_ID" = r."Receiver_ID"
JOIN public."Food_Listing_db" f ON c."Food_ID" = f."Food_ID"
GROUP BY r."Receiver_ID",  r."Name";

SELECT f."Meal_Type", COUNT(c."Claim_ID") AS total_claims
FROM public."Claim_db" c
JOIN public."Food_Listing_db" f ON c."Food_ID" = f."Food_ID"
GROUP BY f."Meal_Type", f."Food_ID"
ORDER BY total_claims DESC
LIMIT 1;

SELECT p."Name", SUM(f."Quantity") AS total_quantity_donated
FROM public."Food_Listing_db" f 
JOIN public."Providers_db" p ON f."Provider_ID" = p."Provider_ID"
GROUP BY p."Provider_ID", p."Name", f."Food_ID"
ORDER BY total_quantity_donated DESC;

SELECT "Food_Name", "Quantity", "Expiry_Date", "Location"
FROM public."Food_Listing_db" f 
WHERE "Expiry_Date" BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '3 days'
ORDER BY "Expiry_Date" ASC;