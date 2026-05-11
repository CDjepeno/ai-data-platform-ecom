{% snapshot snapshot_customers %}

{{
    config(
        target_schema='snapshots',
        unique_key='customer_id',

        strategy='check',
        check_cols=['row_hash'],

        invalidate_hard_deletes=True
    )
}}

SELECT *
FROM {{ ref('stg_customers') }}

{% endsnapshot %}