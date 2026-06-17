from contextlib import contextmanager
from unittest.mock import MagicMock, mock_open, patch


from etl_ecom.scripts.seed.generate_campaign_csv import (
    FIELDNAMES,
    PRODUCT_SKUS,
    _last_id,
    _random_campaign,
    generate,
)

MODULE = "etl_ecom.scripts.seed.generate_campaign_csv"


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_row(campaign_id: str) -> dict:
    return {
        "campaign_id": campaign_id, "campaign_name": "Test", "platform": "meta",
        "owner": "Alice", "product_sku": "SKU-LAPTOP-PRO", "start_date": "2026-01-01",
        "end_date": "2026-02-01", "budget_eur": "1000", "impressions": "10000",
        "clicks": "200", "conversions": "10", "spend_eur": "900", "revenue_eur": "9999",
        "status": "completed",
    }


@contextmanager
def _patch_generate(
    file_exists: bool = False,
    file_size: int = 0,
    reader_side_effect: list | None = None,
):
    """Patch all file I/O in generate() — no disk access."""
    mock_path = MagicMock()
    mock_path.exists.return_value = file_exists
    mock_path.stat.return_value.st_size = file_size
    mock_path.name = "campaigns.csv"

    mock_writer = MagicMock()

    # DictReader is called once per platform when file_exists=True
    readers = reader_side_effect or [iter([]), iter([]), iter([])]

    with patch(f"{MODULE}.CAMPAIGNS_DIR") as mock_dir, \
         patch("builtins.open", mock_open()), \
         patch(f"{MODULE}.csv.DictReader", side_effect=readers), \
         patch(f"{MODULE}.csv.DictWriter", return_value=mock_writer):

        mock_dir.__truediv__.return_value = mock_path
        yield mock_writer, mock_path


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestLastId:

    def test_returns_zero_when_no_rows(self):
        assert _last_id([], "META") == 0

    def test_returns_max_id_from_rows(self):
        rows = [
            {"campaign_id": "META-001"},
            {"campaign_id": "META-005"},
            {"campaign_id": "META-003"},
        ]
        assert _last_id(rows, "META") == 5

    def test_ignores_rows_from_other_prefixes(self):
        rows = [
            {"campaign_id": "META-010"},
            {"campaign_id": "TK-099"},
        ]
        assert _last_id(rows, "META") == 10
        assert _last_id(rows, "TK") == 99


class TestRandomCampaign:

    def test_returns_all_required_fields(self):
        row = _random_campaign("META-001", "meta", "Spring Sale")
        assert set(row.keys()) == set(FIELDNAMES)

    def test_campaign_id_is_set(self):
        row = _random_campaign("META-042", "meta", "Spring Sale")
        assert row["campaign_id"] == "META-042"

    def test_platform_is_set(self):
        row = _random_campaign("TK-001", "tiktok", "Viral Unbox")
        assert row["platform"] == "tiktok"

    def test_product_sku_is_from_catalog(self):
        row = _random_campaign("GGL-001", "google_ads", "Buy Now")
        assert row["product_sku"] in PRODUCT_SKUS

    def test_status_is_valid(self):
        row = _random_campaign("META-001", "meta", "Spring Sale")
        assert row["status"] in {"active", "completed"}

    def test_budget_is_positive(self):
        row = _random_campaign("META-001", "meta", "Spring Sale")
        assert row["budget_eur"] > 0

    def test_spend_does_not_exceed_budget(self):
        row = _random_campaign("META-001", "meta", "Spring Sale")
        assert row["spend_eur"] <= row["budget_eur"]

    def test_clicks_do_not_exceed_impressions(self):
        row = _random_campaign("META-001", "meta", "Spring Sale")
        assert row["clicks"] <= row["impressions"]

    def test_conversions_do_not_exceed_clicks(self):
        row = _random_campaign("META-001", "meta", "Spring Sale")
        assert row["conversions"] <= row["clicks"]

    def test_name_contains_suffix(self):
        row = _random_campaign("META-001", "meta", "Spring Sale")
        assert "Spring Sale" in row["campaign_name"]


class TestGenerate:

    def test_writes_n_rows_per_platform(self):
        with _patch_generate() as (mock_writer, _):
            generate(n=3)

        assert mock_writer.writerows.call_count == 3
        for call_args in mock_writer.writerows.call_args_list:
            assert len(call_args[0][0]) == 3

    def test_writes_header_for_new_file(self):
        with _patch_generate(file_exists=False, file_size=0) as (mock_writer, _):
            generate(n=1)

        assert mock_writer.writeheader.called

    def test_no_header_when_file_already_exists(self):
        with _patch_generate(file_exists=True, file_size=500) as (mock_writer, _):
            generate(n=1)

        assert not mock_writer.writeheader.called

    def test_ids_start_at_one_when_no_existing_rows(self):
        with _patch_generate() as (mock_writer, _):
            generate(n=1)

        meta_rows = mock_writer.writerows.call_args_list[0][0][0]
        assert meta_rows[0]["campaign_id"] == "META-001"

    def test_increments_ids_from_existing_rows(self):
        readers = [
            iter([_make_row("META-007"), _make_row("META-003")]),
            iter([]),
            iter([]),
        ]
        with _patch_generate(file_exists=True, file_size=500, reader_side_effect=readers) as (mock_writer, _):
            generate(n=2)

        meta_rows = mock_writer.writerows.call_args_list[0][0][0]
        ids = [r["campaign_id"] for r in meta_rows]
        assert ids == ["META-008", "META-009"]

    def test_new_rows_have_all_required_fields(self):
        with _patch_generate() as (mock_writer, _):
            generate(n=1)

        meta_rows = mock_writer.writerows.call_args_list[0][0][0]
        assert set(meta_rows[0].keys()) == set(FIELDNAMES)
