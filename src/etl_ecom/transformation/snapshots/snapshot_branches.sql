{% snapshot snapshot_branches %}

{{
    config(
        target_schema='snapshots',
        unique_key='branch_id',

        strategy='check',
        check_cols=['row_hash'],

        invalidate_hard_deletes=True
    )
}}

SELECT *
FROM {{ ref('stg_branches') }}

{% endsnapshot %}