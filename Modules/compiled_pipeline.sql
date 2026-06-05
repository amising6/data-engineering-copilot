SELECT
    user_id AS customer_id,
    CASE 
        WHEN raw_phone IS NOT NULL THEN 
            CASE 
                WHEN LEFT(TRIM(REPLACE(REPLACE(raw_phone, '-', ''), ' ', '')), 2) = '+1' THEN 
                    TRIM(REPLACE(REPLACE(raw_phone, '-', ''), ' ', ''))
                ELSE 
                    '+1' || TRIM(REPLACE(REPLACE(raw_phone, '-', ''), ' ', ''))
            END
        ELSE NULL
    END AS cleaned_phone,
    LOWER(TRIM(email_address)) AS primary_email,
    CONVERT_TIMEZONE('EST', 'UTC', signup_timestamp) AS account_created_dt,
    CASE 
        WHEN account_status_id = 1 THEN TRUE
        ELSE FALSE
    END AS is_active_flag
FROM
    src_users;