import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Pre-migration script to preserve x_origine data before field type change
    """
    _logger.info("Starting pre-migration: Backing up x_origine data")

    # Check if the column exists before trying to copy
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='stock_lot' AND column_name='x_origine'
    """)

    if cr.fetchone():
        # Add temporary column to store old values
        cr.execute("""
            ALTER TABLE stock_lot 
            ADD COLUMN IF NOT EXISTS x_origine_legacy VARCHAR
        """)

        # Copy existing x_origine values to legacy field
        cr.execute("""
            UPDATE stock_lot 
            SET x_origine_legacy = x_origine 
            WHERE x_origine IS NOT NULL
        """)

        # Drop the old x_origine column (it will be recreated as Many2one)
        cr.execute("""
            ALTER TABLE stock_lot 
            DROP COLUMN IF EXISTS x_origine CASCADE
        """)

        cr.commit()
        _logger.info("Pre-migration completed: x_origine data backed up to x_origine_legacy")
    else:
        _logger.info("x_origine column not found, skipping pre-migration")


