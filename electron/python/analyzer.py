import sys
import traceback
import pandas as pd # type: ignore
import json
import re
import copy
import numpy as np
import itertools
import os
from collections import Counter, defaultdict

def join_with_and(items):
    if len(items) == 0:
        return ''
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f'{items[0]} and {items[1]}'
    return ', '.join(items[:-1]) + f', and {items[-1]}'

REPEATED_MEASURES_ANOVA_TABLE_NAMES = [ # [Start Row (included), End Row (excluded)]
    ["Within-Subjects Factors", "Between-Subjects Factors"],
    ["Between-Subjects Factors", "Descriptive Statistics"],
    ["Mauchly's Test of Sphericity", "Tests of Within-Subjects Effects"],
    ["Tests of Within-Subjects Effects", "Tests of Within-Subjects Contrasts"],
    ["Tests of Between-Subjects Effects", "Estimated Marginal Means"]
]
REPEATED_MEASURES_ANOVA_TABLE_NAMES_0 = [table_name[0] for table_name in REPEATED_MEASURES_ANOVA_TABLE_NAMES]
REPEATED_MEASURES_ANOVA_ERROR_MESSAGE = f'The SPSS export sheet must include the following tables: {join_with_and(REPEATED_MEASURES_ANOVA_TABLE_NAMES_0)}'

UNIVARIATE_ANOVA_TABLE_NAMES = [ # [Start Row (included), End Row (excluded)]
    ["Between-Subjects Factors", "Descriptive Statistics"],
    ["Levene's Test of Equality of Error Variances", "Tests of Between-Subjects Effects"],
    ["Tests of Between-Subjects Effects", "Estimated Marginal Means"]
]
UNIVARIATE_ANOVA_TABLE_NAMES_0 = [table_name[0] for table_name in UNIVARIATE_ANOVA_TABLE_NAMES]
UNIVARIATE_ANOVA_ERROR_MESSAGE = f'The SPSS export sheet must include the following tables: {join_with_and(UNIVARIATE_ANOVA_TABLE_NAMES_0)}'
UNIVARIATE_ANOVA_EFFECTS = [
    'Between-subjects Effects'
]

NONPARAMETRIC_TEST_TABLE_NAMES = [ # [Start Row (included), End Row (excluded)]
    ['Ranks', 'Test Statistics'],
    ['Test Statistics', None]
]
NONPARAMETRIC_TEST_TABLE_NAMES_0 = [table_name[0] for table_name in NONPARAMETRIC_TEST_TABLE_NAMES]

KRUSKAL_WALLIS_H_TEST_SECTION_NAME_START_WITH = 'KruskalWallisHTest'
MANN_WHITNEY_U_TEST_SECTION_NAME_START_WITH = 'MannWhitneyUTest'

NONPARAMETRIC_TEST_ERROR_MESSAGE = (
    f'The SPSS Export sheet may contain any number of Kruskal-Wallis and Mann-Whitney U test results.\n\n'

    f'For the Kruskal-Wallis Test, the section names must follow the required format:\n'
    f'"{KRUSKAL_WALLIS_H_TEST_SECTION_NAME_START_WITH}-FactorName123-1ConditionA,2ConditionB,3ConditionC"\n'
    f'The number of conditions must be at least three.\n\n'

    f'For the Mann-Whitney U Test, the section names must follow the required format:\n'
    f'"{MANN_WHITNEY_U_TEST_SECTION_NAME_START_WITH}-FactorName12-1ConditionA,2ConditionB"\n'
    f'or\n'
    f'"{MANN_WHITNEY_U_TEST_SECTION_NAME_START_WITH}-FactorName23-2ConditionB,3ConditionC"\n'
    f'and so on.\n\n'

    f'Each section in the SPSS export sheet must include the following tables: {join_with_and(NONPARAMETRIC_TEST_TABLE_NAMES_0)}.'
)

def verify_group_number_kruskal(group_number:int):
    return group_number >= 3
def verify_group_number_mann(group_number:int):
    return group_number == 2

NONPARAMETRIC_TEST_VALIDATORS = {
    KRUSKAL_WALLIS_H_TEST_SECTION_NAME_START_WITH: verify_group_number_kruskal,
    MANN_WHITNEY_U_TEST_SECTION_NAME_START_WITH: verify_group_number_mann,
}

def has_text(df_str:pd.Series, keyword:str) -> bool:
    return df_str.str.contains(keyword, na=False, regex=False).any()

def get_text_indices(df_str:pd.Series, keyword:str) -> list:
    mask = df_str.str.contains(keyword, na=False, regex=False)
    return df_str.index[mask].tolist()

def get_letters(text: str) -> str:
    match = re.search(r'[A-Za-z]+', text)
    return match.group() if match else ''

def get_digits(text: str) -> str:
    match = re.search(r'[0-9]+', text)
    return match.group() if match else ''

def is_valid_section_name(section_name:str) -> bool:
    section_name = ''.join(section_name.split())

    # StartWith-Factor123-1CondA,2CondB,3CondC
    parts = section_name.split('-')

    if len(parts) != 3:
        return False

    factor_part = parts[1]
    condition_part = parts[2]

    # Factor123
    match = re.fullmatch(r'[A-Za-z]+(\d+)', factor_part)
    if not match:
        return False
    nums_in_factor_part = list(match.group(1))

    # 1CondA,2CondB,3CondC
    items = condition_part.split(',')
    nums_in_condition_part = []

    for item in items:
        match = re.fullmatch(r'(\d+)[A-Za-z]+', item)
        if not match:
            return False
        nums_in_condition_part.append(match.group(1))

    return nums_in_factor_part == nums_in_condition_part

def readDependentVariables(df:pd.DataFrame, df_first_col_str) -> list:
    mask_start = df_first_col_str.str.contains("Test Statistics", na=False, regex=False)
    start_index = df[mask_start].index[0]
    end_index = len(df)
    table = df.iloc[start_index:end_index].reset_index(drop=True)

    FIRST_COL = list(table.iloc[:,0])
    first_data_row = FIRST_COL.index("Mann-Whitney U")
    dpvars = [
        name.replace('_','') for name in list(table.iloc[first_data_row - 1]) 
        if isinstance(name, str)
    ]
    return dpvars

def readBetweenSubjectFactorFromSectionName(section_name:str) -> tuple[str, list]:
    section_name = ''.join(section_name.split())

    parts = section_name.split('-')
    if len(parts) < 3:
        return {}

    factor = get_letters(parts[1])
    conditions_with_digits = parts[2].split(',')
    return factor, conditions_with_digits

def getAllBetweenSubjectFactorsFromSectionName(section_names:list) -> dict:
    bs_dict = {}

    for name in section_names:
        factor, conditions_with_digits = readBetweenSubjectFactorFromSectionName(name)

        if factor not in bs_dict:
            bs_dict[factor] = set()

        bs_dict[factor].update(conditions_with_digits)

    for key in bs_dict:
        bs_dict[key] = [get_letters(text) for text in sorted(bs_dict[key])]

    return bs_dict

def readBetweenSubjectFactorTable(df:pd.DataFrame, df_first_col_str:pd.Series) -> dict:
    try:
        mask_start = df_first_col_str.str.contains("Between-Subjects Factors", na=False, regex=False)
        mask_end = df_first_col_str.str.contains("Descriptive Statistics", na=False, regex=False)
        start_index = df[mask_start].index[0]
        end_index = df[mask_end].index[0] - 1
        table = df.iloc[start_index:end_index].reset_index(drop=True)
    except:
        return {}

    fac_col = table.iloc[2:, 0].reset_index(drop=True).ffill().tolist()
    cond_col = table.iloc[2:, 1].reset_index(drop=True).ffill().tolist()
    bs_dict = defaultdict(list)
    for factor, condition in zip(fac_col, cond_col):
        bs_dict[factor].append(condition)
    bs_dict = dict(bs_dict)

    return bs_dict

def readWithinSubjectFactorTable(df:pd.DataFrame, df_first_col_str:pd.Series) -> dict:
    try:
        mask_start = df_first_col_str.str.contains("Within-Subjects Factors", na=False, regex=False)
        mask_end = df_first_col_str.str.contains("Between-Subjects Factors", na=False, regex=False)
        start_index = df[mask_start].index[0]
        end_index = df[mask_end].index[0] - 1
        table = df.iloc[start_index:end_index].reset_index(drop=True)
    except:
        return {}

    factor_row = list(table.iloc[2,:])
    dpvar_col_index = factor_row.index("Dependent Variable")
    dpvar_col = table.iloc[3:, dpvar_col_index].reset_index(drop=True).ffill().tolist()

    ws_dict = defaultdict(list)
    for dpvar in dpvar_col:
        conditions = dpvar.split('_')
        for i in range(dpvar_col_index):
            if conditions[i] not in ws_dict[factor_row[i]]:
                ws_dict[factor_row[i]].append(conditions[i])
    ws_dict = dict(ws_dict)
    return ws_dict

def getPairWiseTitles(bs_factors:list, ws_factors:list=None):
    if not ws_factors:
        ws_factors = []

    pwc_list = bs_factors
    pwc_list.extend(ws_factors)
    pwc_combs = []
    for r in range(1, len(pwc_list)+1):
        pwc_combs.extend(itertools.combinations(pwc_list, r))
    pwc_combs = [" * ".join(comb) for comb in pwc_combs]

    index = 1
    pwc_titles = []
    for pwc_comb in pwc_combs:
        for _ in range(pwc_comb.count('*') + 1):
            pwc_titles.append(f'{index}. {pwc_comb}')
            index += 1
    pwc_titles.append("Post Hoc Tests")
    return pwc_titles

def canDoNonparametricTest_sub(df_section:pd.Series) -> bool:
    missing_tables = [
        table_name
        for table_name in NONPARAMETRIC_TEST_TABLE_NAMES_0
        if not has_text(df_section, table_name)
    ]
    return len(missing_tables) == 0

def canDoRepeatedMeasuresANOVA(df:pd.DataFrame, df_first_col_str:pd.Series, bs_dict:dict=None, ws_dict:dict=None) -> tuple[dict, dict, dict]:
    for table_name in REPEATED_MEASURES_ANOVA_TABLE_NAMES_0:
        if not has_text(df_first_col_str, table_name):
            return {
                'can_do': False, 
                'err_msg': REPEATED_MEASURES_ANOVA_ERROR_MESSAGE,
                'effects': None
            }, bs_dict, ws_dict

    return {
        'can_do': True, 
        'err_msg': '', 
        'effects': {
            'Between-subjects Effects': list(bs_dict.keys()), 
            'Within-subjects Effects': list(bs_dict.keys()) + list(ws_dict.keys())
        }
    }, bs_dict, ws_dict

def canDoUnivariateANOVA(df:pd.DataFrame, df_first_col_str:pd.Series, bs_dict:dict=None, ws_dict:dict=None) -> tuple[dict, dict, dict]:
    for table_name in UNIVARIATE_ANOVA_TABLE_NAMES_0:
        if not has_text(df_first_col_str, table_name):
            return {
                'can_do': False, 
                'err_msg': UNIVARIATE_ANOVA_ERROR_MESSAGE,
                'effects': None
            }, bs_dict, ws_dict

    return {
        'can_do': True, 
        'err_msg': '', 
        'effects': {
            'Between-subjects Effects': list(bs_dict.keys()),
        }
    }, bs_dict, ws_dict

def canDoNonparametricTest(df:pd.DataFrame, df_first_col_str:pd.Series, bs_dict:dict=None, ws_dict:dict=None) -> tuple[dict, dict, dict]:
    k_indices = get_text_indices(df_first_col_str, KRUSKAL_WALLIS_H_TEST_SECTION_NAME_START_WITH)
    m_indices = get_text_indices(df_first_col_str, MANN_WHITNEY_U_TEST_SECTION_NAME_START_WITH)

    if not (len(k_indices) + len(m_indices)) > 0:
        return {
            'can_do': False, 
            'err_msg': NONPARAMETRIC_TEST_ERROR_MESSAGE,
            'effects': None
        }, bs_dict, ws_dict

    indices = sorted(k_indices + m_indices)

    if len(k_indices) > 0:
        k_section_names = [str(df_first_col_str.iloc[i]) for i in k_indices]
        m_section_names = [str(df_first_col_str.iloc[i]) for i in m_indices]
        k_pair_list = [readBetweenSubjectFactorFromSectionName(x) for x in k_section_names]
        k_factor_set = set(pair[0] for pair in k_pair_list)
        k_condtion_set = set([condition for pair in k_pair_list for condition in pair[1]])
        m_pair_list = [readBetweenSubjectFactorFromSectionName(x) for x in m_section_names]
        m_factor_set = set(pair[0] for pair in m_pair_list)
        m_condtion_set = set([condition for pair in m_pair_list for condition in pair[1]])

        if not (k_factor_set <= m_factor_set and k_condtion_set <= m_condtion_set):
            return {
                'can_do': False, 
                'err_msg': NONPARAMETRIC_TEST_ERROR_MESSAGE,
                'effects': None
            }, bs_dict, ws_dict

    section_names = [str(df_first_col_str.iloc[i]) for i in indices]
    indices.append(len(df_first_col_str)) # end of df

    for i, (id, next_id) in enumerate(zip(indices, indices[1:])):
        if not is_valid_section_name(section_names[i]):
            return {
                'can_do': False, 
                'err_msg': NONPARAMETRIC_TEST_ERROR_MESSAGE,
                'effects': None
            }, bs_dict, ws_dict

        df_section = df_first_col_str.iloc[id:next_id].reset_index(drop=True)
        if not canDoNonparametricTest_sub(df_section):
            return {
                'can_do': False, 
                'err_msg': NONPARAMETRIC_TEST_ERROR_MESSAGE,
                'effects': None
            }, bs_dict, ws_dict

    dpvar_list = readDependentVariables(df, df_first_col_str)
    bs_dict = getAllBetweenSubjectFactorsFromSectionName(section_names)

    return {
        'can_do': True,
        'err_msg': '',
        'dpvar_list': dpvar_list,
        'effects': {name: dpvar_list for name in section_names}
    }, bs_dict, ws_dict

def readMauchlyTest(df:pd.DataFrame, df_first_col_str:pd.Series, ws_dict:dict) -> dict:
    mask_start = df_first_col_str.str.contains("Mauchly's Test of Sphericity", na=False, regex=False)
    mask_end = df_first_col_str.str.contains("Tests of Within-Subjects Effects", na=False, regex=False)
    start_index = df[mask_start].index[0]
    end_index = df[mask_end].index[0] - 1
    table = df.iloc[start_index:end_index].reset_index(drop=True)

    field_names = list(table.iloc[2])
    SIG_COL_IDX = field_names.index('Sig.')
    W_COL_IDX = field_names.index("Mauchly's W")
    CHI2_COL_IDX = field_names.index('Approx. Chi-Square')
    DF_COL_IDX = field_names.index('df')
    SIG_VALS = list(table.iloc[4:, SIG_COL_IDX])[:-1]
    SIG_STRINGS = ["<.001" if v < 0.001 else f"= {v:.3f}" for v in SIG_VALS]
    W_VALS = list(table.iloc[4:, W_COL_IDX])[:-1]
    CHI2_VALS = list(table.iloc[4:, CHI2_COL_IDX])[:-1]
    DF_VALS = list(table.iloc[4:, DF_COL_IDX])[:-1]
    DF_STRINGS = [f"{int(v) if v == int(v) else f'{v:.2f}'}" for v in DF_VALS]

    passed_indices = [
        i for i, x in enumerate(SIG_VALS) \
        if isinstance(x, (int, float)) and x >= 0.05 
    ]
    failed_indices = [
        i for i, x in enumerate(SIG_VALS) \
        if isinstance(x, (int, float)) and x < 0.05 
    ]
    no_test_indices = [
        i for i, x in enumerate(SIG_VALS) \
        if np.isnan(x)
    ]

    fac_col = list(table.iloc[4:, 0].reset_index(drop=True))
    return {
        'passed_conds' : [fac_col[i] for i in passed_indices],
        'passed_values' : ['' for _ in passed_indices],
        'failed_conds' : [fac_col[i] for i in failed_indices],
        'failed_values' : [
            f'Mauchly\'s Test (Failed): W = {W_VALS[i]:.3f}, \\chi^2({DF_STRINGS[i]}) = {CHI2_VALS[i]:.2f}, p {SIG_STRINGS[i]}'
            for i in failed_indices
        ],
        'no_test_conds': [fac_col[i] for i in no_test_indices],
        'no_test_values': [
            f"Mauchly's Test (No result)"
            if any(len(ws_dict[factor]) > 2 for factor in fac_col[i].replace('*', ' ').split())
            else ''
            for i in no_test_indices
        ],
    }

def readLeveneTest(df:pd.DataFrame, df_first_col_str:pd.Series) -> str:
    mask_start = df_first_col_str.str.contains("Levene's Test of Equality of Error Variances", na=False, regex=False)
    mask_end = df_first_col_str.str.contains("Tests of Between-Subjects Effects", na=False, regex=False)
    start_index = df[mask_start].index[0]
    end_index = df[mask_end].index[0] - 1
    table = df.iloc[start_index:end_index].reset_index(drop=True)

    field_names = list(table.iloc[1])
    SIG_COL_IDX = field_names.index('Sig.')
    F_COL_IDX = field_names.index("Levene Statistic")
    DF1_COL_IDX = field_names.index('df1')
    DF2_COL_IDX = field_names.index('df2')
    SIG_VAL = list(table.iloc[2:, SIG_COL_IDX])[0]
    SIG_STRING = "<.001" if SIG_VAL < 0.001 else f"= {SIG_VAL:.3f}"
    F = list(table.iloc[2:, F_COL_IDX])[0]
    DF1 = list(table.iloc[2:, DF1_COL_IDX])[0]
    DF2 = list(table.iloc[2:, DF2_COL_IDX])[0]
    DF1_STRING = f"{int(DF1) if DF1 == int(DF1) else f'{DF1:.2f}'}"
    DF2_STRING = f"{int(DF2) if DF2 == int(DF2) else f'{DF2:.2f}'}"

    return f'Levene\'s Test: F({DF1_STRING},{DF2_STRING}) = {F:.3f}, p {SIG_STRING}' if SIG_VAL < 0.05 else ''

def readTestsOfBetweenSubjectEffects(df:pd.DataFrame, df_first_col_str:pd.Series, levene_res:str=None) -> dict:
    mask_start = df_first_col_str.str.contains("Tests of Between-Subjects Effects", na=False, regex=False)
    mask_end = df_first_col_str.str.contains("Estimated Marginal Means", na=False, regex=False)
    start_index = df[mask_start].index[0]
    end_index = df[mask_end].index[0] - 1
    table = df.iloc[start_index:end_index].reset_index(drop=True)

    row_index = list(table.iloc[:, 5]).index('Sig.')
    field_names = list(table.iloc[row_index])
    sig_col_index = field_names.index('Sig.')
    sig_values = list(table.iloc[5:, sig_col_index])
    sig_values = [x for x in sig_values if not np.isnan(x)]
    sig_indices = [
        i for i, x in enumerate(sig_values) \
        if isinstance(x, (int, float)) and x < 0.05 
    ]
    potential_indices = [
        i for i, x in enumerate(sig_values) \
        if isinstance(x, (int, float)) and x >= 0.05 and x < 0.1
    ]
    fac_comb_col = list(table.iloc[5:, 0].reset_index(drop=True))

    return {
        'sig_conds'             : [fac_comb_col[i] for i in sig_indices],
        'sig_values'            : [sig_values[i]   for i in sig_indices],
        'sig_homogeneous'       : [levene_res      for _ in sig_indices],
        'potential_conds'       : [fac_comb_col[i] for i in potential_indices],
        'potential_values'      : [sig_values[i]   for i in potential_indices],
        'potential_homogeneous' : [levene_res      for _ in potential_indices],
    }

def readTestsOfWithinSubjectEffects(df:pd.DataFrame, df_first_col_str:pd.Series, mauchly_dict:dict, bs_dict:dict) -> dict:
    mask_start = df_first_col_str.str.contains("Tests of Within-Subjects Effects", na=False, regex=False)
    mask_end = df_first_col_str.str.contains("Tests of Within-Subjects Contrasts", na=False, regex=False)
    start_index = df[mask_start].index[0]
    end_index = df[mask_end].index[0] - 1
    table = df.iloc[start_index:end_index].reset_index(drop=True)

    field_names = list(table.iloc[4])
    sig_col_index = field_names.index('Sig.')
    sig_values = list(table.iloc[5:, sig_col_index])
    sig_indices = [
        i for i, x in enumerate(sig_values) \
        if isinstance(x, (int, float)) and x < 0.05 
    ]
    potential_indices = [
        i for i, x in enumerate(sig_values) \
        if isinstance(x, (int, float)) and x >= 0.05 and x < 0.1
    ]
    potential_values = [sig_values[i] for i in potential_indices]
    sig_values = [sig_values[i] for i in sig_indices]

    fac_comb_col = table.iloc[5:, 0].reset_index(drop=True).ffill().tolist()
    correction_col = table.iloc[5:, 1].reset_index(drop=True)
    sig_fac_combs = [fac_comb_col[i]  for i in sig_indices]
    sig_corrections = [correction_col[i] for i in sig_indices]
    potential_fac_combs = [fac_comb_col[i]  for i in potential_indices]
    potential_corrections = [correction_col[i] for i in potential_indices]

    result = {
        'sig_conds'       : [],
        'sig_values'      : [],
        'sig_homogeneous' : [],
        'potential_conds' : [],
        'potential_values': [],
        'potential_homogeneous' : []
    }

    failed_conds = mauchly_dict['failed_conds']
    failed_values = mauchly_dict['failed_values']
    no_test_conds = mauchly_dict['no_test_conds']
    no_test_values = mauchly_dict['no_test_values']

    for comb, value, correction in zip(sig_fac_combs, sig_values, sig_corrections):
        if result['sig_conds'] and comb == result['sig_conds'][-1]:
            continue
        comb_remove_bs = "*".join(
            x.strip()
            for x in comb.split("*")
            if x.strip() and not any(r in x.strip() for r in bs_dict)
        )
        if comb_remove_bs.startswith('Error('):
            continue
        failed_cond_idx = failed_conds.index(comb_remove_bs) if comb_remove_bs in failed_conds else -1
        no_test_cond_idx = no_test_conds.index(comb_remove_bs) if comb_remove_bs in no_test_conds else -1
        if failed_cond_idx >= 0 and correction != "Greenhouse-Geisser":
            continue

        result['sig_conds'].append(comb)
        result['sig_values'].append(value)

        if failed_cond_idx >= 0:
            result['sig_homogeneous'].append(f'{failed_values[failed_cond_idx]}, Greenhouse-Geisser')
        elif no_test_cond_idx >= 0:
            result['sig_homogeneous'].append(f'{no_test_values[no_test_cond_idx]}')
        else:
            result['sig_homogeneous'].append('')

    for comb, value, correction in zip(potential_fac_combs, potential_values, potential_corrections):
        if result['potential_conds'] and comb == result['potential_conds'][-1]:
            continue

        comb_remove_bs = "*".join(
            x.strip()
            for x in comb.split("*")
            if x.strip() and not any(r in x.strip() for r in bs_dict)
        )
        if comb_remove_bs.startswith('Error('):
            continue
        failed_cond_idx = failed_conds.index(comb_remove_bs) if comb_remove_bs in failed_conds else -1
        no_test_cond_idx = no_test_conds.index(comb_remove_bs) if comb_remove_bs in no_test_conds else -1
        if failed_cond_idx >= 0 and correction != "Greenhouse-Geisser":
            continue

        result['potential_conds'].append(comb)
        result['potential_values'].append(value)

        if failed_cond_idx >= 0:
            result['potential_homogeneous'].append(f'{failed_values[failed_cond_idx]}, Greenhouse-Geisser')
        elif no_test_cond_idx >= 0:
            result['potential_homogeneous'].append(f'{no_test_values[no_test_cond_idx]}')
        else:
            result['potential_homogeneous'].append('')

    return result

def readPairwiseComparison(df:pd.DataFrame, df_first_col_str:pd.Series, ws_dict:dict=None) -> str:
    mask_pwc = df_first_col_str.str.contains("Pairwise Comparisons", na=False, regex=False)
    mask_uni = df_first_col_str.str.contains("Univariate Tests", na=False, regex=False)
    mask_multi = df_first_col_str.str.contains("Multivariate Tests", na=False, regex=False)
    start_index = df[mask_pwc].index[0]
    try:
        end_index = df[mask_multi].index[0] - 1
    except:
        end_index = df[mask_uni].index[0] - 1
    table = df.iloc[start_index:end_index].reset_index(drop=True)

    field_names = list(table.iloc[2])
    sig_col_index = next((
        i for i, field_name in enumerate(field_names)
        if 'Sig.' in field_name
    ), -1)
    if sig_col_index < 0:
        return None
    sig_values = list(table.iloc[4:, sig_col_index])
    sig_values = [x for x in sig_values if not np.isnan(x)]
    sig_indices = [
        i for i, x in enumerate(sig_values) \
        if isinstance(x, (int, float)) and x < 0.05 
    ]
    potential_indices = [
        i for i, x in enumerate(sig_values) \
        if isinstance(x, (int, float)) and x >= 0.05 and x < 0.1
    ]

    diff_col_index = field_names.index('Mean Difference (I-J)')
    sig_conds = []
    potential_conds = []
    for i in range(diff_col_index + 1):
        factor = field_names[i].split()[-1]
        cond_col = table.iloc[4:, i].reset_index(drop=True).ffill().tolist()

        if ws_dict and factor in ws_dict:
            sub_sig_conds = [ws_dict[factor][int(cond_col[i]) - 1] for i in sig_indices]
            sub_potential_conds = [ws_dict[factor][int(cond_col[i]) - 1] for i in potential_indices]
        else:
            sub_sig_conds = [cond_col[i] for i in sig_indices]
            sub_potential_conds = [cond_col[i] for i in potential_indices]

        sig_conds.append(sub_sig_conds)
        potential_conds.append(sub_potential_conds)

    potential_values = [sig_values[i] for i in potential_indices]
    sig_values = [sig_values[i] for i in sig_indices]

    result_list = []
    sig_msg_list = []
    for value, *conds in zip(sig_values, *sig_conds):
        direction = str(conds[-1])
        direction = float(direction.split('*')[0])
        conds = copy.deepcopy(conds[:-1])

        result = set(conds)
        if result in result_list:
            continue
        result_list.append(result)
        sig_value = float(value)
        sig = "<.001" if sig_value < 0.001 else f"{sig_value:.3f}"
        star = "***" if sig_value < 0.001 else "**" if sig_value < 0.01 else "*"

        sig_str = f"{star}({sig}) "
        for i in range(len(conds)-2):
            sig_str += f"In {conds[i]}, "
        if direction > 0:
            sig_str += f"{conds[-2]} > {conds[-1]}"
        else:
            sig_str += f"{conds[-1]} > {conds[-2]}"
        sig_msg_list.append(sig_str)

    for value, *conds in zip(potential_values, *potential_conds):
        direction = str(conds[-1])
        direction = float(direction.split('*')[0])
        conds = copy.deepcopy(conds[:-1])
        result = set(conds)
        if result in result_list:
            continue
        result_list.append(result)
        potential_str = f"potential({float(value):.3f}) "

        for i in range(len(conds)-2):
            potential_str += f"In {conds[i]}, "
        if direction > 0:
            potential_str += f"{conds[-2]} > {conds[-1]}"
        else:
            potential_str += f"{conds[-1]} > {conds[-2]}"
        sig_msg_list.append(potential_str)
    return sig_msg_list

def readPWCSections(df:pd.DataFrame, df_first_col_str:pd.Series, pair_wise_titles:list, bs_effects:dict, ws_effects:dict=None, ws_dict:dict=None) -> dict:
    bs_sig_mapping = {
        cond: {
            'value': value,
            'homogeneous': homogeneous
        }
        for cond, value, homogeneous in zip(
            bs_effects['sig_conds'],
            bs_effects['sig_values'],
            bs_effects['sig_homogeneous'],
        )
    }
    bs_potential_mapping = {
        cond: {
            'value': value,
            'homogeneous': homogeneous
        }
        for cond, value, homogeneous in zip(
            bs_effects['potential_conds'],
            bs_effects['potential_values'],
            bs_effects['potential_homogeneous'],
        )
    }
    if ws_effects:
        ws_sig_mapping = {
            cond: {
                'value': value,
                'homogeneous': homogeneous
            }
            for cond, value, homogeneous in zip(
                ws_effects['sig_conds'],
                ws_effects['sig_values'],
                ws_effects['sig_homogeneous'],
            )
        }
        ws_potential_mapping = {
            cond: {
                'value': value,
                'homogeneous': homogeneous
            }
            for cond, value, homogeneous in zip(
                ws_effects['potential_conds'],
                ws_effects['potential_values'],
                ws_effects['potential_homogeneous'],
            )
        }
    else:
        ws_sig_mapping = {}
        ws_potential_mapping = {}

    result = {}

    for i, title in enumerate(pair_wise_titles):

        cond = re.sub(r'^\d+\.\s*', '', title)
        cond_set = set(cond.replace('*', ' ').split())

        cond_in_dict = next((
            x for x in bs_sig_mapping.keys()
            if set(x.replace('*', ' ').split()) == cond_set
        ), None)

        if cond_in_dict is None:
            cond_in_dict = next((
                x for x in ws_sig_mapping.keys()
                if set(x.replace('*', ' ').split()) == cond_set
            ), None)

        if cond_in_dict is not None:
            mask_start = df_first_col_str.str.contains(title, na=False, regex=False)
            mask_end = df_first_col_str.str.contains(pair_wise_titles[i+1], na=False, regex=False)
            start_index = df[mask_start].index[0]
            end_index = df[mask_end].index[0] - 1
            table = df.iloc[start_index:end_index].reset_index(drop=True)
            sig_msg_list = readPairwiseComparison(table, table.iloc[:,0].astype(str), ws_dict)
            sig_value = float(bs_sig_mapping[cond_in_dict]['value']) if cond_in_dict in bs_sig_mapping else float(ws_sig_mapping[cond_in_dict]['value'])
            sig = "<.001" if sig_value < 0.001 else f"{sig_value:.3f}"
            star = "***" if sig_value < 0.001 else "**" if sig_value < 0.01 else "*"
            sig_str = f"{star}({sig}) {cond}"
            homogeneous = bs_sig_mapping[cond_in_dict]['homogeneous'] \
                          if cond_in_dict in bs_sig_mapping and isinstance(bs_sig_mapping[cond_in_dict]['homogeneous'], str) \
                          else ''
            homogeneous += ws_sig_mapping[cond_in_dict]['homogeneous'] \
                           if cond_in_dict in ws_sig_mapping and isinstance(ws_sig_mapping[cond_in_dict]['homogeneous'], str) \
                           else ''
            if sig_str not in result:
                result[sig_str] = []
            result[sig_str].append((homogeneous, sig_msg_list))

        else:
            cond_in_dict = next((
                x for x in bs_potential_mapping.keys()
                if set(x.replace('*', ' ').split()) == cond_set
            ), None)

            if cond_in_dict is None:
                cond_in_dict = next((
                    x for x in ws_potential_mapping.keys()
                    if set(x.replace('*', ' ').split()) == cond_set
                ), None)

            if cond_in_dict is None:
                continue

            mask_start = df_first_col_str.str.contains(title, na=False, regex=False)
            mask_end = df_first_col_str.str.contains(pair_wise_titles[i+1], na=False, regex=False)
            start_index = df[mask_start].index[0]
            end_index = df[mask_end].index[0] - 1
            table = df.iloc[start_index:end_index].reset_index(drop=True)
            potential_msg_list = readPairwiseComparison(table, table.iloc[:,0].astype(str), ws_dict)
            potential_value = float(bs_potential_mapping[cond_in_dict]['value']) if cond_in_dict in bs_potential_mapping else float(ws_potential_mapping[cond_in_dict]['value'])
            potential_str = f"potential({float(potential_value):.3f}) {cond}"
            homogeneous = bs_potential_mapping[cond_in_dict]['homogeneous'] \
                          if cond_in_dict in bs_potential_mapping and isinstance(bs_potential_mapping[cond_in_dict]['homogeneous'], str) \
                          else ''
            homogeneous += ws_potential_mapping[cond_in_dict]['homogeneous'] \
                           if cond_in_dict in ws_potential_mapping and isinstance(ws_potential_mapping[cond_in_dict]['homogeneous'], str) \
                           else ''
            if potential_str not in result:
                result[potential_str] = []
            result[potential_str].append((homogeneous, potential_msg_list))
    return result

def readMannWhitneyRanks(df:pd.DataFrame, df_first_col_str:pd.Series, dpvar:str, conditions_with_digits:list) -> str:
    cond_dict = {get_digits(x): get_letters(x) for x in conditions_with_digits}

    mask_start = df_first_col_str.str.contains("Ranks", na=False, regex=False)
    mask_end = df_first_col_str.str.contains("Test Statistics", na=False, regex=False)
    start_index = df[mask_start].index[0]
    end_index = df[mask_end].index[0] - 1
    table = df.iloc[start_index:end_index].reset_index(drop=True)

    FIRST_COL = list(table.iloc[:, 0])
    DPVAR_ROW_IDX = next(
        (i for i, item in enumerate(FIRST_COL) if isinstance(item, str) and item.replace('_', '') == dpvar),
        -1
    )
    if DPVAR_ROW_IDX == -1:
        print(f'[readMannWhitneyRanks]: dpvar row not found.', file=sys.stderr)
        return None

    COND_IDX_1 = str(table.iloc[DPVAR_ROW_IDX, 1])
    COND_IDX_2 = str(table.iloc[DPVAR_ROW_IDX + 1, 1])
    RANK_1 = float(table.iloc[DPVAR_ROW_IDX, 3])
    RANK_2 = float(table.iloc[DPVAR_ROW_IDX + 1, 3])

    if RANK_1 > RANK_2:
        return f"{cond_dict[COND_IDX_1]} > {cond_dict[COND_IDX_2]}"
    else:
        return f"{cond_dict[COND_IDX_2]} > {cond_dict[COND_IDX_1]}"

def readKruskalWallisHTestStatistics(df:pd.DataFrame, df_first_col_str:pd.Series, factor:str) -> dict:
    mask_start = df_first_col_str.str.contains("Test Statistics", na=False, regex=False)
    start_index = df[mask_start].index[0]
    end_index = len(df)
    table = df.iloc[start_index:end_index].reset_index(drop=True)

    FIRST_COL = list(table.iloc[:, 0])
    SIG_ROW_IDX = next(
        (i for i, item in enumerate(FIRST_COL) if isinstance(item, str) and 'Sig.' in item),
        -1
    )
    if SIG_ROW_IDX == -1:
        print(f'[readKruskalWallisHTestStatistics]: sig row not found.', file=sys.stderr)
        return None
    SIG_ROW = list(table.iloc[SIG_ROW_IDX, :])

    SECOND_COL = list(table.iloc[:, 1])
    DPVAR_ROW_IDX = next(
        (i for i, item in enumerate(SECOND_COL) if isinstance(item, str)),
        -1
    )
    if DPVAR_ROW_IDX == -1:
        print(f'[readKruskalWallisHTestStatistics]: dpvar row not found.', file=sys.stderr)
        return None
    DPVAR_ROW = [x.replace('_', '') if isinstance(x, str) else x for x in list(table.iloc[DPVAR_ROW_IDX, :])]

    SIG_INDICES = [
        i for i, x in enumerate(SIG_ROW) 
        if isinstance(x, (int, float)) and not np.isnan(x) and x < 0.05
    ]
    POTENTIAL_INDICES = [
        i for i, x in enumerate(SIG_ROW) 
        if isinstance(x, (int, float)) and not np.isnan(x) and x >= 0.05 and x < 0.1
    ]
    SIG_DPVARS = [DPVAR_ROW[i] for i in SIG_INDICES]
    SIG_VALS = [SIG_ROW[i] for i in SIG_INDICES]
    POTENTIAL_DPVARS = [DPVAR_ROW[i] for i in POTENTIAL_INDICES]
    POTENTIAL_VALS = [SIG_ROW[i] for i in POTENTIAL_INDICES]

    results = {}

    for dpvar, value in zip(SIG_DPVARS, SIG_VALS):
        sig_value = float(value)
        sig = "<.001" if sig_value < 0.001 else f"{sig_value:.3f}"
        star = "***" if sig_value < 0.001 else "**" if sig_value < 0.01 else "*"
        sig_str = f'{star}({sig})'
        results[dpvar] = f'{sig_str} {factor}'

    for dpvar, value in zip(POTENTIAL_DPVARS, POTENTIAL_VALS):
        sig_str = f'potential({float(value):.3f})'
        results[dpvar] = f'{sig_str} {factor}'

    return results

def readMannWhitneyTestStatistics(df:pd.DataFrame, df_first_col_str:pd.Series, factor:str, conditions_with_digits:list, k_result:dict=None) -> dict:
    mask_start = df_first_col_str.str.contains("Test Statistics", na=False, regex=False)
    start_index = df[mask_start].index[0]
    end_index = len(df)
    table = df.iloc[start_index:end_index].reset_index(drop=True)

    FIRST_COL = list(table.iloc[:, 0])
    SIG_ROW_IDX = next(
        (i for i, item in enumerate(FIRST_COL) if isinstance(item, str) and 'Sig.' in item),
        -1
    )
    if SIG_ROW_IDX == -1:
        print(f'[readMannWhitneyTestStatistics]: sig row not found.', file=sys.stderr)
        return None
    SIG_ROW = list(table.iloc[SIG_ROW_IDX, :])

    second_col = list(table.iloc[:, 1])
    DPVAR_ROW_IDX = next(
        (i for i, item in enumerate(second_col) if isinstance(item, str)),
        -1
    )
    if DPVAR_ROW_IDX == -1:
        print(f'[readMannWhitneyTestStatistics]: dpvar row not found.', file=sys.stderr)
        return None
    DPVAR_ROW = [x.replace('_', '') if isinstance(x, str) else x for x in list(table.iloc[DPVAR_ROW_IDX, :])]
    DPVAR_LIST = [x for x in DPVAR_ROW if isinstance(x, str)]

    if k_result is None:
        bonferroni = 1
    else:
        bonferroni = 3

    SIG_INDICES = [
        i for i, x in enumerate(SIG_ROW) 
        if isinstance(x, (int, float)) and not np.isnan(x) and x * bonferroni < 0.05
    ]
    POTENTIAL_INDICES = [
        i for i, x in enumerate(SIG_ROW) 
        if isinstance(x, (int, float)) and not np.isnan(x) and x * bonferroni >= 0.05 and x * bonferroni < 0.1
    ]
    SIG_DPVARS = [DPVAR_ROW[i] for i in SIG_INDICES]
    SIG_VALS = [SIG_ROW[i] * bonferroni for i in SIG_INDICES]
    POTENTIAL_DPVARS = [DPVAR_ROW[i] for i in POTENTIAL_INDICES]
    POTENTIAL_VALS = [SIG_ROW[i] * bonferroni for i in POTENTIAL_INDICES]

    results = {dpvar: {} for dpvar in DPVAR_LIST}

    for dpvar, value in zip(SIG_DPVARS, SIG_VALS):
        if k_result is not None and dpvar not in k_result:
            continue

        sig_value = min(1, float(value))
        sig = "<.001" if sig_value < 0.001 else f"{sig_value:.3f}"
        star = "***" if sig_value < 0.001 else "**" if sig_value < 0.01 else "*"
        sig_str = f'{star}({sig})'
        effect = f'{sig_str} {factor}' if k_result is None else k_result[dpvar]
        result = readMannWhitneyRanks(df, df_first_col_str, dpvar, conditions_with_digits)

        if effect not in results[dpvar]:
            results[dpvar][effect] = []
        results[dpvar][effect].append(f'{sig_str} {result}')

    for dpvar, value in zip(POTENTIAL_DPVARS, POTENTIAL_VALS):
        if k_result is not None and dpvar not in k_result:
            continue

        sig_value = min(1, float(value))
        sig_str = f'potential({sig_value:.3f})'
        effect = f'{sig_str} {factor}' if k_result is None else k_result[dpvar]
        result = readMannWhitneyRanks(df, df_first_col_str, dpvar, conditions_with_digits)

        if dpvar not in results:
            results[dpvar] = {}
        if effect not in results[dpvar]:
            results[dpvar][effect] = []
        results[dpvar][effect].append(f'{sig_str} {result}')

    return results

def getDescriptiveStatistics(data_df:pd.DataFrame, bs_items:dict, ws_items:dict, dpvar:str):
    field_names = [
        col for col in data_df.columns 
        if '_' in col and dpvar in col and 
        all(key in col for key in ws_items.values())
    ]

    bs_mask = pd.Series(True, index=data_df.index)
    for factor, condition in bs_items.items():
        bs_mask &= (data_df[factor] == condition)
    filtered_df = data_df[bs_mask]

    mean_df = filtered_df[field_names].mean(axis=1)
    mean = np.mean(mean_df)
    std = np.std(mean_df, ddof=1)
    mdn = np.median(mean_df)
    iqr = np.percentile(mean_df, 75) - np.percentile(mean_df, 25)

    return field_names, round(float(mean), 2), round(float(std), 2), round(float(mdn), 2), round(float(iqr), 2)

def getEstimates(data_df:pd.DataFrame, spss_df:pd.DataFrame, df_first_col_str:pd.Series, args:dict, query_src_name: str, bs_dict:dict, ws_dict:dict) -> list:
    pairwise_titles = getPairWiseTitles(list(bs_dict.keys()), list(ws_dict.keys()))
    query_pwc_title = next((
        title for title in pairwise_titles 
        if set(query_src_name.replace('*', ' ').split()) == set((' '.join(title.split()[1:]).replace('*', ' ').split())))
    , None)

    if not query_pwc_title:
        return None

    mask_start = df_first_col_str.str.contains(query_pwc_title, na=False, regex=False)
    start_index = spss_df[mask_start].index[0]
    table = spss_df.iloc[start_index:].reset_index(drop=True)
    mask_start = table.iloc[:,0].astype(str).str.contains("Estimates", na=False, regex=False)
    mask_end = table.iloc[:,0].astype(str).str.contains("Pairwise Comparisons", na=False, regex=False)
    start_index = table[mask_start].index[0]
    end_index = table[mask_end].index[0] - 1
    table = table.iloc[start_index:end_index].reset_index(drop=True)
    field_names = list(table.iloc[2])

    MEAN_COL_INDEX = field_names.index('Mean')
    MEAN_LIST = [x for x in list(table.iloc[:, MEAN_COL_INDEX]) if isinstance(x, (int, float)) and not np.isnan(x)]
    ROW_COUNT = len(MEAN_LIST)
    FACTORS = field_names[:MEAN_COL_INDEX]
    CONDITIONS = [
        table.iloc[4:4+ROW_COUNT, i].ffill().tolist()
        for i in range(len(FACTORS))
    ]

    result = []
    for i in range(ROW_COUNT):
        item = {
            FACTORS[idx]: CONDITIONS[idx][i] 
                if not str(CONDITIONS[idx][i]).isdigit() 
                else ws_dict[FACTORS[idx]][int(CONDITIONS[idx][i]) - 1]
            for idx in range(len(FACTORS))
        }
        item['factors'] = FACTORS
        bs_items = {k: v for k, v in item.items() if k in bs_dict}
        ws_items = {k: v for k, v in item.items() if k in ws_dict}

        item['Data_Fields'], item['Mean_Data'], item['STD_Data'], item['Median_Data'], item['IQR_Data'] = \
            getDescriptiveStatistics(data_df, bs_items, ws_items, args['dpvar'])
        item['MeanSD'] = f'($M = {item['Mean_Data']:.2f}, SD = {item['STD_Data']:.2f}$)'
        item['MdnIQR'] = f'($Mdn = {item['Median_Data']:.2f}, IQR = {item['IQR_Data']:.2f}$)'
        item['Mean_EST'] = round(MEAN_LIST[i], 2)

        if item['Mean_Data'] == item['Mean_EST']:
            item['err_msg'] = ''
        else:
            item['err_msg'] = f"Raw mean ({item['Mean_Data']:.2f}) and estimated mean ({item['Mean_EST']:.2f}) differ, possibly due to non-independent User Data columns or unbalanced group sizes."

        result.append(item)

    return result

def queryANOVASigResultTable(data_df:pd.DataFrame, spss_df:pd.DataFrame, spss_df_first_col_str:pd.Series, args:dict) -> dict:
    result = {}
    EFFECT = args['effect']
    bs_dict = readBetweenSubjectFactorTable(spss_df, spss_df_first_col_str)
    ws_dict = readWithinSubjectFactorTable(spss_df, spss_df_first_col_str)
    df_row_offset = 0
    mauchly_res = None

    if EFFECT == 'Between-subjects Effects':
        mask_start = spss_df_first_col_str.str.contains("Tests of Between-Subjects Effects", na=False, regex=False)
        mask_end = spss_df_first_col_str.str.contains("Estimated Marginal Means", na=False, regex=False)
        start_index = spss_df[mask_start].index[0]
        end_index = spss_df[mask_end].index[0] - 1
        table = spss_df.iloc[start_index:end_index].reset_index(drop=True)
        sources = list(table.iloc[:, 0])
        field_col_idx = sources.index('Source')
        field_names = list(table.iloc[field_col_idx])
    else: # Within-subjects Effects
        mask_start = spss_df_first_col_str.str.contains("Tests of Within-Subjects Effects", na=False, regex=False)
        mask_end = spss_df_first_col_str.str.contains("Tests of Within-Subjects Contrasts", na=False, regex=False)
        start_index = spss_df[mask_start].index[0]
        end_index = spss_df[mask_end].index[0] - 1
        table = spss_df.iloc[start_index:end_index].reset_index(drop=True)
        sources = list(table.iloc[:, 0])
        field_col_idx = sources.index('Source')
        field_names = list(table.iloc[field_col_idx])
        mauchly_res = readMauchlyTest(spss_df, spss_df_first_col_str, ws_dict)

    DF_COL_INDEX = field_names.index('df')
    F_COL_INDEX = field_names.index('F')
    SIG_COL_INDEX = field_names.index('Sig.')
    ETA_COL_INDEX = field_names.index('Partial Eta Squared')

    query_factor_set = set(args['options'])
    ws_factors = [factor for factor in ws_dict.keys() if factor in query_factor_set]

    if mauchly_res is not None:
        failed_cond_sets = [set(comb.replace('*', ' ').split()) for comb in mauchly_res['failed_conds']]
        if set(ws_factors) in failed_cond_sets:
            df_row_offset = 1 # Check Greenhouse-Geisser

    sources = list(table.iloc[:, 0])
    src_factor_sets = [set(x.replace('*', ' ').split()) if isinstance(x, str) else x for x in sources]
    DF1_ROW_INDEX = src_factor_sets.index(query_factor_set) + df_row_offset
    QUERY_SRC_NAME = str(table.iloc[DF1_ROW_INDEX - df_row_offset, 0])
    src_df2 = next((x for x in sources if isinstance(x, str) and 'Error' in x and all(key in x for key in ws_factors)), None)
    DF2_ROW_INDEX = sources.index(src_df2) + df_row_offset

    DF1 = float(table.iloc[DF1_ROW_INDEX, DF_COL_INDEX])
    DF2 = float(table.iloc[DF2_ROW_INDEX, DF_COL_INDEX])
    DF1_STRING = f"{int(DF1) if DF1 == int(DF1) else f'{DF1:.2f}'}"
    DF2_STRING = f"{int(DF2) if DF2 == int(DF2) else f'{DF2:.2f}'}"
    F = float(table.iloc[DF1_ROW_INDEX, F_COL_INDEX])
    F_STRING = f"{F:.3f}"
    P = float(table.iloc[DF1_ROW_INDEX, SIG_COL_INDEX])
    P_STRING = 'p < .001' if P < 0.001 else f'p = ' + f'{P:.3f}'.lstrip("0")
    ETA = float(table.iloc[DF1_ROW_INDEX, ETA_COL_INDEX])
    ETA_STRING = f'{ETA:.3f}'.lstrip("0")

    test_statistics = f"$F({DF1_STRING},{DF2_STRING}) = {F_STRING}, {P_STRING}, \\eta_p^2 = {ETA_STRING}$"
    if df_row_offset:
        test_statistics += ", Greenhouse-Geisser corrected"
    result['test_statistics'] = [test_statistics]
    result['descriptive_statistics'] = getEstimates(data_df, spss_df, spss_df_first_col_str, args, QUERY_SRC_NAME, bs_dict, ws_dict)
    return result

def getKruskalWallisHTestStatistics(rank_table:pd.DataFrame, test_table:pd.DataFrame) -> str:
    RANK_FIRST_COL = [x.replace('_', '') if isinstance(x, str) else x for x in list(rank_table.iloc[:, 0])]
    RANK_DPVAR_ROW_IDX = RANK_FIRST_COL.index(args['dpvar'])
    N_ROW_IDX = RANK_DPVAR_ROW_IDX + 2

    _, cols = np.where(rank_table == 'N')
    N = float(rank_table.iloc[N_ROW_IDX, cols[0]])

    TEST_DPVAR_ROW_IDX = next(
        (i for i, item in enumerate(list(test_table.iloc[:, 1])) if isinstance(item, str)),
        -1
    )
    TEST_DPVAR_ROW = [x.replace('_', '') if isinstance(x, str) else x for x in list(test_table.iloc[TEST_DPVAR_ROW_IDX, :])]
    TEST_DPVAR_COL_IDX = TEST_DPVAR_ROW.index(args['dpvar'])

    TEST_FIRST_COL = list(test_table.iloc[:, 0])
    H_ROW_IDX = TEST_FIRST_COL.index('Kruskal-Wallis H')
    H = float(test_table.iloc[H_ROW_IDX, TEST_DPVAR_COL_IDX])
    DF_ROW_IDX = TEST_FIRST_COL.index('df')
    DF = float(test_table.iloc[DF_ROW_IDX, TEST_DPVAR_COL_IDX])
    DF_STRING = f"{int(DF) if DF == int(DF) else f'{DF:.2f}'}"
    P_ROW_IDX = next(
        (i for i, item in enumerate(TEST_FIRST_COL) if isinstance(item, str) and 'Sig.' in item),
        -1
    )
    P = float(test_table.iloc[P_ROW_IDX, TEST_DPVAR_COL_IDX])
    P_STRING = 'p < .001' if P < 0.001 else f'p = ' + f'{P:.3f}'.lstrip("0")
    K = DF + 1
    ETA = (H - K + 1) / (N - K)
    ETA_STRING = '\\eta_H^2 < .01' if ETA < 0.01 else f'\\eta_H^2 = ' + f'{ETA:.2f}'.lstrip("0")

    return f'$H({DF_STRING}) = {H:.3f}, {P_STRING}, {ETA_STRING}$'

def getMannWhitneyTestStatistics(rank_table:pd.DataFrame, test_table:pd.DataFrame, bonferroni:int) -> str:
    RANK_FIRST_COL = [x.replace('_', '') if isinstance(x, str) else x for x in list(rank_table.iloc[:, 0])]
    RANK_DPVAR_ROW_IDX = RANK_FIRST_COL.index(args['dpvar'])
    N_ROW_IDX = RANK_DPVAR_ROW_IDX + 2

    _, cols = np.where(rank_table == 'N')
    N = float(rank_table.iloc[N_ROW_IDX, cols[0]])

    TEST_DPVAR_ROW_IDX = next(
        (i for i, item in enumerate(list(test_table.iloc[:, 1])) if isinstance(item, str)),
        -1
    )
    TEST_DPVAR_ROW = [x.replace('_', '') if isinstance(x, str) else x for x in list(test_table.iloc[TEST_DPVAR_ROW_IDX, :])]
    TEST_DPVAR_COL_IDX = TEST_DPVAR_ROW.index(args['dpvar'])

    TEST_FIRST_COL = list(test_table.iloc[:, 0])
    U_ROW_IDX = TEST_FIRST_COL.index('Mann-Whitney U')
    U = float(test_table.iloc[U_ROW_IDX, TEST_DPVAR_COL_IDX])
    Z_ROW_IDX = TEST_FIRST_COL.index('Z')
    Z = float(test_table.iloc[Z_ROW_IDX, TEST_DPVAR_COL_IDX])
    P_ROW_IDX = next(
        (i for i, item in enumerate(TEST_FIRST_COL) if isinstance(item, str) and 'Sig.' in item),
        -1
    )
    P = min(1, float(test_table.iloc[P_ROW_IDX, TEST_DPVAR_COL_IDX]) * bonferroni)
    P_STRING = 'p < .001' if P < 0.001 else f'p = ' + f'{P:.3f}'.lstrip("0")
    R_STRING = f'{float(abs(Z / np.sqrt(N))):.2f}'.lstrip('0')

    return f'$U = {U:.1f}, {P_STRING}, r = {R_STRING}$'

def queryNonparametricSigResultTable(data_df:pd.DataFrame, spss_df:pd.DataFrame, spss_df_first_col_str:pd.Series, args:dict) -> dict:
    result = {}
    EFFECT = args['effect']
    k_rank_table = None
    k_test_table = None
    bonferroni = 1

    if MANN_WHITNEY_U_TEST_SECTION_NAME_START_WITH in EFFECT:
        factor, _ = readBetweenSubjectFactorFromSectionName(EFFECT)
        mask_k = (
            spss_df_first_col_str.str.contains(KRUSKAL_WALLIS_H_TEST_SECTION_NAME_START_WITH, na=False, regex=False)
            &
            spss_df_first_col_str.str.contains(factor, na=False, regex=False)
        )
        if mask_k.any():
            start_index = spss_df[mask_k].index[0]
            end_index = len(spss_df_first_col_str)
            k_table = spss_df.iloc[start_index:end_index].reset_index(drop=True)
            k_table_first_col_str = k_table.iloc[:, 0].astype(str)
            k_mask_rank = k_table_first_col_str.str.contains("Ranks", na=False, regex=False)
            k_mask_test = k_table_first_col_str.str.contains("Test Statistics", na=False, regex=False)
            k_rank_index = k_table[k_mask_rank].index[0]
            k_test_index = k_table[k_mask_test].index[0]
            k_end_index = len(k_table_first_col_str)
            k_rank_table = k_table.iloc[k_rank_index:k_test_index - 1].reset_index(drop=True)
            k_test_table = k_table.iloc[k_test_index:k_end_index].reset_index(drop=True)
            bonferroni = 3

    mask_start = spss_df_first_col_str.str.contains(EFFECT, na=False, regex=False)
    start_index = spss_df[mask_start].index[0]
    end_index = len(spss_df_first_col_str)
    table = spss_df.iloc[start_index:end_index].reset_index(drop=True)
    table_first_col_str = table.iloc[:, 0].astype(str)

    mask_rank = table_first_col_str.str.contains("Ranks", na=False, regex=False)
    mask_test = table_first_col_str.str.contains("Test Statistics", na=False, regex=False)

    start_index = table[mask_rank].index[0]
    end_index = table[mask_test].index[0] - 1
    rank_table = table.iloc[start_index:end_index].reset_index(drop=True)

    start_index = table[mask_test].index[0]
    end_index = len(table)
    test_table = table.iloc[start_index:end_index].reset_index(drop=True)

    result['test_statistics'] = []

    if k_test_table is not None:
        result['test_statistics'].append(getKruskalWallisHTestStatistics(k_rank_table, k_test_table))

    result['test_statistics'].append(
        getMannWhitneyTestStatistics(rank_table, test_table, bonferroni) \
            if MANN_WHITNEY_U_TEST_SECTION_NAME_START_WITH in EFFECT \
            else getKruskalWallisHTestStatistics(rank_table, test_table)
    )

    bs_dict = getAllBetweenSubjectFactorsFromSectionName([EFFECT])
    result['descriptive_statistics'] = []

    for factor, conditions in bs_dict.items():
        for condtion in conditions:
            item = {}
            item['factors'] = [factor]
            item[factor] = condtion
            item['Data_Fields'], item['Mean_Data'], item['STD_Data'], item['Median_Data'], item['IQR_Data'] = \
                getDescriptiveStatistics(data_df, bs_items={ factor: condtion }, ws_items={}, dpvar=args['dpvar'])
            item['MeanSD'] = f'($M = {item['Mean_Data']:.2f}, SD = {item['STD_Data']:.2f}$)'
            item['MdnIQR'] = f'($Mdn = {item['Median_Data']:.2f}, IQR = {item['IQR_Data']:.2f}$)'
            item['err_msg'] = ''
            result['descriptive_statistics'].append(item)
    
    return result

def getRepeatedMeasuresANOVASigResultTable(df:pd.DataFrame, df_first_col_str:pd.Series, bs_dict:dict=None, ws_dict:dict=None):
    pair_wise_titles = getPairWiseTitles(list(bs_dict.keys()), list(ws_dict.keys()))
    mauchly_dict = readMauchlyTest(df, df_first_col_str, ws_dict)
    bs_effects = readTestsOfBetweenSubjectEffects(df, df_first_col_str)
    ws_effects = readTestsOfWithinSubjectEffects(df, df_first_col_str, mauchly_dict, bs_dict)
    sig_results = readPWCSections(df, df_first_col_str, pair_wise_titles, bs_effects, ws_effects, ws_dict)
    return sig_results

def getUnivariateANOVASigResultTable(df:pd.DataFrame, df_first_col_str:pd.Series, bs_dict:dict=None, ws_dict:dict=None):
    pair_wise_titles = getPairWiseTitles(list(bs_dict.keys()))
    levene_res = readLeveneTest(df, df_first_col_str)
    bs_effects = readTestsOfBetweenSubjectEffects(df, df_first_col_str, levene_res)
    sig_results = readPWCSections(df, df_first_col_str, pair_wise_titles, bs_effects)
    return sig_results

def getNonparametricSigResultTable(df:pd.DataFrame, df_first_col_str:pd.Series, bs_dict:dict=None, ws_dict:dict=None):
    k_indices = get_text_indices(df_first_col_str, KRUSKAL_WALLIS_H_TEST_SECTION_NAME_START_WITH)
    k_section_names = [str(df_first_col_str.iloc[i]) for i in k_indices]
    k_bs_dict = getAllBetweenSubjectFactorsFromSectionName(k_section_names)
    k_indices.append(len(df_first_col_str)) # end of df

    m_indices = get_text_indices(df_first_col_str, MANN_WHITNEY_U_TEST_SECTION_NAME_START_WITH)
    m_section_names = [str(df_first_col_str.iloc[i]) for i in m_indices]
    m_indices.append(len(df_first_col_str)) # end of df
    sig_results = {}

    for i, (m_id, m_next_id) in enumerate(zip(m_indices, m_indices[1:])):
        m_df_section = df.iloc[m_id:m_next_id].reset_index(drop=True)
        factor, conditions_with_digits = readBetweenSubjectFactorFromSectionName(m_section_names[i])
        k_results = None

        if factor in k_bs_dict:
            j = next(j for j, x in enumerate(k_section_names) if factor in x.split('-')[1])
            k_df_section = df.iloc[k_indices[j]:k_indices[j + 1]].reset_index(drop=True)
            k_results = readKruskalWallisHTestStatistics(
                k_df_section, k_df_section.iloc[:, 0].astype(str), factor
            )

        try:
            temp_results = readMannWhitneyTestStatistics(
                m_df_section, m_df_section.iloc[:, 0].astype(str), factor, conditions_with_digits, k_results
            )
        except Exception as err:
            error_msg = traceback.format_exc()
            print(f'{error_msg}', file=sys.stderr)

        for dpvar, effect_results in temp_results.items():
            if dpvar not in sig_results:
                sig_results[dpvar] = {}

            for effect, result_list in effect_results.items():
                if effect in sig_results[dpvar]:
                    sig_results[dpvar][effect].extend(result_list)
                else:
                    sig_results[dpvar][effect] = result_list

    return sig_results

ANALYSIS_METHOD = [
    ('Repeated Measures ANOVA', canDoRepeatedMeasuresANOVA, getRepeatedMeasuresANOVASigResultTable, queryANOVASigResultTable),
    ('Univariate ANOVA', canDoUnivariateANOVA, getUnivariateANOVASigResultTable, queryANOVASigResultTable),
    ('Nonparametric (Kruskal-Wallis Test, Mann-Whitney U Test)', canDoNonparametricTest, getNonparametricSigResultTable, queryNonparametricSigResultTable),
]
ANALYSIS_METHOD_NAMES = [
    method[0] for method in ANALYSIS_METHOD
]
ANALYSIS_MAPPING = {
    name: (check_func, result_func, query_func)
    for name, check_func, result_func, query_func in ANALYSIS_METHOD
}

def getFactorDicts(bs_items:list, ws_items:list) -> dict:
    result = {
        'bs_dict': {},
        'ws_dict': {},
    }

    for item in bs_items:
        factor = item['factor']
        condition = item['condition']
        if factor not in result['bs_dict']:
            result['bs_dict'][factor] = []
        result['bs_dict'][factor].append(condition)
    for key in result['bs_dict']:
        result['bs_dict'][key].sort()

    for item in ws_items:
        factor = item['factor']
        condition = item['condition']
        if factor not in result['ws_dict']:
            result['ws_dict'][factor] = []
        result['ws_dict'][factor].append(condition)
    for key in result['ws_dict']:
        result['ws_dict'][key].sort()

    return result

def read_sheet_names_and_types(result_path, spss_export_filepath):
    result = {}
    dfs = pd.read_excel(spss_export_filepath, sheet_name=None, header=None, engine="openpyxl")
    DEFAULT_ANALYSIS_METHOD_KEY = 'Verification failed'
    DEFAULT_ANALYSIS_METHOD_VAL = { 'can_do': False, 'err_msg': 'Invalid SPSS Export sheet format. Please refer to the Guide for the format required by each method.'}
    used_methods = Counter()

    for name, df in dfs.items():
        df_first_col_str = df.iloc[:, 0].astype(str)
        bs_dict = readBetweenSubjectFactorTable(df, df_first_col_str)
        ws_dict = readWithinSubjectFactorTable(df, df_first_col_str)

        checker_res = {
            method: checker(df, df_first_col_str, bs_dict, ws_dict)
            for method, checker, _, _ in ANALYSIS_METHOD
        }
        result[name] = {
            method: checker_res[method][0]
            for method, _, _, _ in ANALYSIS_METHOD
        }
        result[name][DEFAULT_ANALYSIS_METHOD_KEY] = DEFAULT_ANALYSIS_METHOD_VAL

        result[name]['Analysis Method'] = next(
            (method for method, _, _, _ in ANALYSIS_METHOD if result[name][method]['can_do']),
            DEFAULT_ANALYSIS_METHOD_KEY
        )
        used_methods[result[name]['Analysis Method']] += 1

        for method, _, _, _ in ANALYSIS_METHOD:
            if len(bs_dict) == 0:
                bs_dict = checker_res[method][1]
            if len(ws_dict) == 0:
                ws_dict = checker_res[method][2]

        result[name]['bs_dict'] = bs_dict
        result[name]['ws_dict'] = ws_dict

    method_options = list(used_methods.most_common(2))
    most_used_method = next((x[0] for x in method_options if x[0] in ANALYSIS_METHOD_NAMES), DEFAULT_ANALYSIS_METHOD_KEY)

    for sheet in result.keys():
        result[sheet]['Analysis Method'] = most_used_method
        result[sheet]['dpvar_list'] = result[sheet][most_used_method].get('dpvar_list', [])

    with open(os.path.join(result_path, 'result.json'), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

def read_user_data(result_path, filepath):
    result = {}
    dfs = pd.read_excel(filepath, sheet_name=None, header=0, engine="openpyxl")

    for name, df in dfs.items():
        variables = [col for col in df.columns if '_' in col]
        dependent_variables = [v.split('_')[-1] for v in variables]
        result[name] = list(dict.fromkeys(dependent_variables))

    with open(os.path.join(result_path, 'result.json'), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

def verify_user_data(result_path, filepath, sheet_name_list, bs_items, ws_items):
    result = {
        'success': True,
        'err_msg': '',
    }

    factor_dicts = getFactorDicts(bs_items, ws_items)

    for sheet_name in sheet_name_list:
        df = pd.read_excel(filepath, sheet_name=sheet_name, header=0, engine="openpyxl")
        cur_err_msg = []

        for bs_factor in factor_dicts['bs_dict'].keys():
            if bs_factor not in df.columns:
                cur_err_msg.append(f'> Unexpected Between-subjects Factor: "{bs_factor}" is not found in data fields.')
            else:
                for bs_condition in factor_dicts['bs_dict'][bs_factor]:
                    if bs_condition not in set(df[bs_factor]):
                        cur_err_msg.append(f'> Unexpected Between-subjects Condition: "{bs_condition}" is not found in "{bs_factor}".')
                for bs_condition in set(df[bs_factor]):
                    if bs_condition not in factor_dicts['bs_dict'][bs_factor]:
                        cur_err_msg.append(f'> Missed Between-subjects Condition: "{bs_condition}" is not found in "{bs_factor}".')
        ws_conditions = [
            condition
            for conditions in factor_dicts['ws_dict'].values()
            for condition in conditions
        ]
        ws_conditions = list(dict.fromkeys(ws_conditions))
        variables = [col for col in df.columns if '_' in col]
        ws_conditions_in_df = [
            condition
            for prefix in variables
            for condition in prefix.split("_")[:-1]
        ]
        ws_conditions_in_df = list(dict.fromkeys(ws_conditions_in_df))
        Missing = [x for x in ws_conditions_in_df if x not in ws_conditions]
        for x in Missing:
            if x:
                cur_err_msg.append(f'> Missing: "{x}" should be defined as a within-subjects condition')

        if cur_err_msg:
            if result['err_msg']:
                result['err_msg'] += '\n\n'
            result['err_msg'] += f'Sheet "{sheet_name}" is not valid to use:\n' + '\n'.join(cur_err_msg)

    result['success'] = not result['err_msg']

    with open(os.path.join(result_path, 'result.json'), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

def get_anova_sig_result_table(dfs:dict, method_dict:dict) -> pd.DataFrame:
    rows = []
    last_dpvar = ''
    last_factor_str = ''
    category_has_result = set()
    dpvar_has_result = set()

    for sheet_name, df in dfs.items():
        df_first_col_str = df.iloc[:, 0].astype(str)
        bs_dict = readBetweenSubjectFactorTable(df, df_first_col_str)
        ws_dict = readWithinSubjectFactorTable(df, df_first_col_str)
        method = method_dict[sheet_name]['Analysis Method']
        sig_results = ANALYSIS_MAPPING[method][1](df, df_first_col_str, bs_dict, ws_dict)

        category = method_dict[sheet_name]['category']
        if category in category_has_result:
            category = ''

        factors = list(bs_dict.keys())
        factors.extend(list(ws_dict.keys()))
        tmp_factor_str = ' * '.join(factors)
        factor_str = '' if tmp_factor_str == last_factor_str else tmp_factor_str
        last_factor_str = tmp_factor_str

        dpvar = method_dict[sheet_name]['dpvar_name']
        if dpvar in dpvar_has_result:
            dpvar = ''
        else:
            factor_str = tmp_factor_str

        if last_dpvar != '' and dpvar != last_dpvar and last_dpvar not in dpvar_has_result:
            category_has_result.add(category)
            rows.append([category, last_dpvar, last_factor_str, '', 'No significant Result', ''])

        last_dpvar = method_dict[sheet_name]['dpvar_name']
        is_row_added = False

        for effect, result_list in sig_results.items():
            for result in result_list:
                homogeneous = result[0]
                sig_list = result[1]

                for sig_str in sig_list:
                    if not is_row_added:
                        rows.append([category, dpvar, factor_str, homogeneous, effect, sig_str])
                        is_row_added = True
                        category_has_result.add(category)
                        dpvar_has_result.add(dpvar)
                    else:
                        rows.append(['', '', '', homogeneous, effect, sig_str])

    return pd.DataFrame(rows, columns=['Category', 'Dependent Variable', 'Factor', 'Homogeneous', 'Effect', 'Result'])

def get_mann_sig_result_table(dfs:dict, method_dict:dict) -> pd.DataFrame:
    rows = []
    category_has_result = set()
    dpvar_has_result = set()

    for sheet_name, df in dfs.items():
        df_first_col_str = df.iloc[:, 0].astype(str)
        method = method_dict[sheet_name]['Analysis Method']
        sig_results = ANALYSIS_MAPPING[method][1](df, df_first_col_str)

        for dpvar, effect_results in sig_results.items():
            category = sheet_name if sheet_name not in category_has_result else ''
            dpvar = dpvar if dpvar not in dpvar_has_result else ''

            if len(effect_results) == 0:
                category_has_result.add(category)
                rows.append([category, dpvar, 'No significant Result', ''])
                continue

            is_row_added = False
            for effect, result_list in effect_results.items():
                for result in result_list:
                    if not is_row_added:
                        rows.append([category, dpvar, effect, result])
                        is_row_added = True
                        category_has_result.add(category)
                        dpvar_has_result.add(dpvar)
                    else:
                        rows.append(['', '', effect, result])

    return pd.DataFrame(rows, columns=['Category', 'Dependent Variable', 'Effect', 'Result'])

def get_sig_result_table(result_path, spss_export_filepath, method_dict):
    dfs = pd.read_excel(spss_export_filepath, sheet_name=None, header=None, engine="openpyxl")

    if 'ANOVA' in list(method_dict.values())[0]['Analysis Method']:
        output_df = get_anova_sig_result_table(dfs, method_dict)
    elif 'Mann' in list(method_dict.values())[0]['Analysis Method']:
        output_df = get_mann_sig_result_table(dfs, method_dict)

    try:
        with pd.ExcelWriter(os.path.join(result_path, 'result.xlsx'), mode="a", if_sheet_exists="replace", engine="openpyxl") as writer:
            output_df.to_excel(writer, sheet_name='Significant Results', index=False)
    except FileNotFoundError:
        with pd.ExcelWriter(os.path.join(result_path, 'result.xlsx'), mode="w", engine="openpyxl") as writer:
            output_df.to_excel(writer, sheet_name='Significant Results', index=False)

def query_analysis_detail(result_path, user_data_path, spss_export_path, args) -> dict:
    data_df = pd.read_excel(user_data_path, sheet_name=args['data_sheet'], header=0, engine="openpyxl")
    spss_df = pd.read_excel(spss_export_path, sheet_name=args['spss_sheet'], header=None, engine="openpyxl")
    spss_df_first_col_str = spss_df.iloc[:,0].astype(str)

    try:
        result = ANALYSIS_MAPPING[args['method']][2](data_df, spss_df, spss_df_first_col_str, args)
    except Exception as err:
        error_msg = traceback.format_exc()
        print(f'{error_msg}', file=sys.stderr)
        return

    with open(os.path.join(result_path, 'result.json'), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

if __name__ == '__main__':
    action = sys.argv[1]
    result_path = sys.argv[2]

    if action == 'read_user_data':
        filepath = sys.argv[3]
        read_user_data(result_path, filepath)
    elif action == 'verify_user_data':
        filepath = sys.argv[3]
        sheet_name_list = json.loads(sys.argv[4])
        bs_items = json.loads(sys.argv[5])
        ws_items = json.loads(sys.argv[6])
        verify_user_data(result_path, filepath, sheet_name_list, bs_items, ws_items)
    elif action == 'read_sheet_names_and_types':
        spss_export_filepath = sys.argv[3]
        read_sheet_names_and_types(result_path, spss_export_filepath)
    elif action == 'get-sig-result-table':
        spss_export_filepath = sys.argv[3]
        method_dict = json.loads(sys.argv[4])
        get_sig_result_table(result_path, spss_export_filepath, method_dict)
    elif action == 'query-analysis-detail':
        user_data_path = sys.argv[3]
        spss_export_path = sys.argv[4]
        args = json.loads(sys.argv[5])
        query_analysis_detail(result_path, user_data_path, spss_export_path, args)
