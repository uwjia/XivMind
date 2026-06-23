"""Subject-related utilities for table naming and subject handling."""

SUPPORTED_SUBJECTS = ['cs', 'q-fin', 'stat', 'econ', 'q-bio']
DEFAULT_SUBJECT = 'cs'


def subject_to_table_prefix(subject: str) -> str:
    """
    Convert subject to table prefix.

    Args:
        subject: Subject identifier (e.g., 'cs', 'q-fin', 'stat')

    Returns:
        Table prefix string (e.g., '', 'q_fin_', 'stat_')

    Examples:
        'cs' -> '' (empty prefix for backward compatibility)
        'q-fin' -> 'q_fin_'
        'stat' -> 'stat_'
    """
    if subject == 'cs':
        return ''  # No prefix for default subject (backward compatibility)

    # Replace hyphen with underscore
    return subject.replace('-', '_') + '_'


def get_subject_table_name(base_table: str, subject: str) -> str:
    """
    Get subject-specific table name.

    Args:
        base_table: Base table name (e.g., 'papers', 'date_index')
        subject: Subject identifier (e.g., 'cs', 'q-fin', 'stat')

    Returns:
        Subject-specific table name

    Examples:
        ('papers', 'cs') -> 'papers'
        ('papers', 'q-fin') -> 'q_fin_papers'
        ('papers', 'stat') -> 'stat_papers'
    """
    prefix = subject_to_table_prefix(subject)
    return prefix + base_table


def is_valid_subject(subject: str) -> bool:
    """Check if subject is a valid supported subject."""
    return subject in SUPPORTED_SUBJECTS