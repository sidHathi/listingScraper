from QueryParams import LeaseTerm

keywordMap: dict[str, LeaseTerm] = {
    "short-term": LeaseTerm.ShortTerm,
    "short term": LeaseTerm.ShortTerm,
    "shortTerm": LeaseTerm.ShortTerm,
    "variable": LeaseTerm.ShortTerm,
    "month-to-month": LeaseTerm.MonthToMonth,
    "month to month": LeaseTerm.MonthToMonth,
    "long term": LeaseTerm.LongTerm,
    "long-term": LeaseTerm.LongTerm,
}

termToMonthMap: dict[LeaseTerm, int | None] = {
    LeaseTerm.MonthToMonth: 1,
    LeaseTerm.ShortTerm: 4,
    LeaseTerm.DateRange: None,
    LeaseTerm.LongTerm: 12,
    LeaseTerm.Specific: None
}