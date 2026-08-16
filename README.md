## SPSS Result Reader Guide

Welcome to the SPSS Results Reader! 👋

If you've ever spent way too much time digging through SPSS output just to find out which results are significant, this tool is here to make things a little easier.

SPSS Results Reader helps you quickly find significant results in your analysis, and also lets you easily check test statistics and descriptive statistics without having to search through the output yourself.

Hopefully, this makes reading your SPSS results a bit less painful and saves you some time!

## Table of Contents

- [Getting Started](#getting-started)
    - [1. Download the App](#1-download-the-app)
    - [2. Install the App](#2-install-the-app)
- [Create a User Data Excel File in the Required Format](#create-a-user-data-excel-file-in-the-required-format)
    - [Between-subjects Factors](#between-subjects-factors)
    - [Within-subjects Factors](#within-subjects-factors)
    - [Dependent Variables](#dependent-variables)
    - [1. One Row per User](#1-one-row-per-user)
    - [2. Data Fields (Columns)](#2-data-fields-columns)
    - [3. Naming the Columns](#3-naming-the-columns)
    - [4. Summary](#4-summary)
- [Create a Factors.json File](#create-a-factorsjson-file)
    - [Validate User Data Steps](#validate-user-data-steps)
- [Validate Your User Data File Format](#validate-your-user-data-file-format)
- [Perform SPSS Analysis](#perform-spss-analysis)
    - [Repeated Measures ANOVA](#repeated-measures-anova)
    - [Univariate ANOVA](#univariate-anova)
    - [Mann-Whitney U Test](#mann-whitney-u-test)
    - [Kruskal-Wallis Test](#kruskal-wallis-test)
    - [Export Analysis Results](#export-analysis-results)
- [Create a New Project in the System](#create-a-new-project-in-the-system)
    - [New Project Steps](#new-project-steps)
- [Export Significant Results](#export-significant-results)
    - [Repeated Measures ANOVA and Univariate ANOVA](#repeated-measures-anova-and-univariate-anova)
    - [Nonparametric Tests (Mann-Whitney U Test or Kruskal-Wallis H Test)](#nonparametric-tests-mann-whitney-u-test-or-kruskal-wallis-h-test)
- [Query Analysis Details](#query-analysis-details)
    - [Test Statistics](#test-statistics)
    - [Descriptive Statistics](#descriptive-statistics)
- [Data Management](#data-management)
    - [Editing Factor Data](#editing-factor-data)
    - [Deleting Data](#deleting-data)

## Getting Started

### 1. Download the App

Go to the Github **Releases** page and download the installer that matches your operating system.

Choose the appropriate file for your computer:

* **Windows** → SPSS-Results-Reader-Windows
* **macOS** → SPSS-Results-Reader-macOS

### 2. Install the App

* **Windows** → Open the .exe file to install the app.
* **macOS** → Open the .dmg file and install the app.

That's it! You're ready to go. 🎉

[back to toc](#table-of-contents)

## Create a User Data Excel File in the Required Format

Before creating your Excel file, it's important to understand the difference between **Between-subjects Factors**, **Within-subjects Factors**, and **Dependent Variables**.

### Between-subjects Factors

A **Between-subjects Factor** is a factor where each participant belongs to **only one level** of the factor.

For example, participants may be divided into different groups, with each participant assigned to only one group.

### Within-subjects Factors

A **Within-subjects Factor** is a factor where **the same participant experiences multiple levels** of the factor.

For example, the same participant may complete tasks under several different conditions.

### Dependent Variables

A **Dependent Variable** is the outcome or measurement that is collected from each participant.

It is the variable that you want to **measure, compare, or analyze** to determine whether it changes under different conditions.

For example, a dependent variable could be a participant's **reaction time, accuracy, rating, or physiological measurement**.

In short:

* **Between-subjects Factors** → Each participant belongs to only one level.
* **Within-subjects Factors** → Each participant experiences multiple levels.
* **Dependent Variables** → The outcomes or measurements collected for analysis.

Before importing your data, make sure your user data are organized in an Excel file (**.xlsx** or **.xls**) that follows the required format.

[back to toc](#table-of-contents)

### 1. One Row per User

Each row must correspond to **exactly one user/participant**.

For example, if your study contains 30 participants, the Excel file should contain 30 data rows, excluding the header row.

| UserID | AgeGroup | TrainingMethod | Accuracy | ResponseTime |
| ------ | -------- | -------------- | -------: | -----------: |
| 001    | Young    | MethodA        |     0.82 |     0.82     |
| 002    | Older    | MethodB        |     0.91 |     0.91     |
| 003    | Young    | MethodA        |     0.76 |     0.76     |

Do **not** create multiple rows for the same user to represent different experimental conditions. All data belonging to the same user should be stored in the same row.

### 2. Data Fields (Columns)

The columns in your Excel file should include:

* All **Between-subjects Factors**
* All **Dependent Variables**
* Dependent variables separated according to the levels of any **Within-subjects Factors**

For example, suppose a study has:

* Between-subjects factors:
  * **AgeGroup**: Young, Older
  * **TrainingMethod**: MethodA, MethodB, MethodC
* Within-subjects factors:
  * **TaskType**: Memory, Reaction, Attention
  * **Difficulty**: Easy, Hard
* Dependent variables:
  * **Accuracy**
  * **ResponseTime**

Because **TaskType** and **Difficulty** are within-subjects factors, each of the dependent variable should be separated according to **each combination of their levels**:

| UserID | AgeGroup | TrainingMethod | Memory_Easy_Accuracy | Memory_Hard_Accuracy | Reaction_Easy_Accuracy | Reaction_Hard_Accuracy | Attention_Easy_Accuracy | Attention_Hard_Accuracy | ... |
| ------- | --------- | --------------- | -------------------: | -------------------: | ---------------------: | ---------------------: | ----------------------: | ----------------------: | --- |
| 001     | Young     | MethodA        |                 0.82 |                 0.76 |                   0.91 |                   0.85 |                    0.88 |                    0.79 | ... |
| 002     | Older     | MethodB        |                 0.75 |                 0.68 |                   0.84 |                   0.77 |                    0.81 |                    0.72 | ... |
| 003     | Young     | MethodA        |                 0.89 |                 0.83 |                   0.94 |                   0.88 |                    0.92 |                    0.86 | ... |


In this example, each participant has data for all **3 TaskType × 2 Difficulty = 6 within-subjects conditions**.

### 3. Naming the Columns

Each column should have a **unique and descriptive name**.

For dependent variables associated with within-subjects factors, the column name should follow this structure:

**`OneOfTheConditionInTheFirstFactor_OneOfTheConditionInTheSecondFactor_DependentVariable`**

For example:

* **Memory_Easy_ResponseTime**
* **Memory_Hard_ResponseTime**
* **Reaction_Easy_ResponseTime**
* **Reaction_Hard_ResponseTime**
* **Attention_Easy_ResponseTime**
* **Attention_Hard_ResponseTime**

The conditions in the column name must be ordered according to the order of the corresponding factors. The Dependent Variable should always appear at the end of the column name. **The underscore `_` must be used exclusively as the separator, and all spaces must be removed.**

You do not need to use all Within-subjects Factors for every Dependent Variable. Include only the Within-subjects Factors that are relevant to each Dependent Variable based on your research design.

> **Important Notes**
> 1. **Avoid using the same column name for multiple conditions.**
>    Each column should have a unique name that clearly identifies the corresponding conditions and dependent variable.
> 2. **Keep the number of columns consistent with the selected Within-subjects Factors.**
>    Once you decide to divide a Dependent Variable according to a specific set of Within-subjects Factors, all data fields containing that Dependent Variable must follow the same division.
>    - For example, if **ResponseTime** is divided according to **3 TaskType × 2 Difficulty = 6 within-subjects conditions**, there must be exactly **six columns** containing **ResponseTime**. These six columns should represent the six mutually exclusive subsets of the original **ResponseTime** data.
> 3. **Use a separate Excel data sheet when different grouping schemes are necessary.**
>    If the same Dependent Variable needs to be divided using different sets of Within-subjects Factors, do not combine these different grouping schemes in the same data sheet. Instead, create a **new Excel data sheet** for the alternative grouping scheme.

### 4. Summary

Your Excel file should follow these basic principles:

* **One row = one user**
* **One column = one data field**
* Include all **Between-subjects Factors**
* Include all **Dependent Variables**
* For **Within-subjects Factors**, separate dependent variables according to the relevant factor levels or combinations of levels
* Place the **Dependent Variable at the end** of the column name
* Use **unique and descriptive column names**
* Use a separate Excel data sheet when different grouping schemes are necessary.

Following this format allows the software to correctly identify the experimental design and organize the data for statistical analysis.

[back to toc](#table-of-contents)

## Create a Factors.json File

To help the system better understand your User Data Excel file, you need to create a **.json** file that describes all of your **Between-subjects Factors** and **Within-subjects Factors**.

For example, suppose your experiment has the following factors:

- **Between-subjects factors:**
  - **AgeGroup**: Young, Older
  - **TrainingMethod**: MethodA, MethodB, MethodC
- **Within-subjects factors:**
  - **TaskType**: Memory, Reaction, Attention
  - **Difficulty**: Easy, Hard

Your **Factors.json** should be:

```json
{
  "Between-subjects Factor": {
    "AgeGroup": [
      "Young",
      "Older"
    ],
    "TrainingMethod": [
      "MethodA",
      "MethodB"
      "MethodC"
    ]
  },
  "Within-subjects Factor": {
    "TaskType": [
      "Memory",
      "Reaction",
      "Attention"
    ],
    "Difficulty": [
      "Easy",
      "Hard"
    ]
  }
}
```

If you also use additional conditions to group some dependent variables, please include them under **Within-subjects Factor** as well.

[back to toc](#table-of-contents)

## Validate Your User Data File Format

After completing your **User Data Excel file** and **Factors.json**, you can first go to **Project > New Project** to validate whether your data meets the required format and conditions. Once the data has been successfully validated, you can proceed with the **SPSS Analysis**.

### Validate User Data Steps

1. **Enter Project Name**  
   Enter a name for your project. At this stage, you can choose any name you prefer.

2. **Select Factor Setting**  
   Click **`+`** to select your prepared **Factors.json** file, or simply drag and drop the file into the window.

   If your **.json** file does not follow the required format and cannot be imported, you can click **`+ pencil`** to create or edit the **Factors.json** directly within the system.

3. **Select User Data**  
   Click **`+`** to select your prepared **User Data Excel file**, or simply drag and drop the file into the window.

4. **Select Sheets and Validate Your Data**  
   The system will display all **sheet names** in your selected User Data Excel file. Select the sheets you want to use for SPSS analysis. Multiple sheets can be selected.

   After selecting the sheets, click **`Apply`**.

   - **If your User Data Excel file meets the required format:**  
     The system will display all **dependent variables** identified from your User Data Excel file on the right side. If everything looks correct, you can proceed with **SPSS Analysis** using this setup.

   - **If your User Data Excel file does not meet the required format:**  
     The system will display the corresponding **Error Messages** on the right side. Please modify your **User Data Excel file** or **Factors.json** according to the error messages, and validate the data again until the format is correct.

> **Note:** You do not need to perform an analysis on every dependent variable. There is also no limit on how many times you can perform SPSS Analysis. Please select the dependent variables and perform analyses according to your research needs.

> **Note:** On the **New Project** page, you can press **`Enter`** to proceed to the next step, or use the **`←` and `→` arrow keys** to navigate between pages.

[back to toc](#table-of-contents)

## Perform SPSS Analysis

Before proceeding, please make sure that **IBM SPSS Statistics** is installed on your computer.

This system currently supports the interpretation of results from the following four types of analyses:

- **Repeated Measures ANOVA**: Use this method when your data needs to be analyzed using both **Between-subjects factors** and **Within-subjects factors**, or using **Within-subjects factors** only.

- **Univariate ANOVA**: Use this method when your data only needs to be analyzed using **Between-subjects factors**.

- **Mann–Whitney U Test**: Use this method when your data are **non-continuous and ordinal**, such as questionnaire scores. The analysis is performed by grouping the data using **Between-subjects factors**, and only **two groups** can be compared at a time.

- **Kruskal–Wallis Test**: Use this method when your data are **non-continuous and ordinal**, such as questionnaire scores. The analysis is performed by grouping the data using **Between-subjects factors**, and **more than two groups** can be compared at a time.

The following sections will introduce, step by step, how to use **IBM SPSS Statistics** to perform these four types of analyses and how to export the results as an Excel file.

### Repeated Measures ANOVA

1. Open **IBM SPSS Statistics**, import your **User Data Excel file**, and select the sheet you want to use.

2. Select **Analyze > General Linear Model > Repeated Measures**.

3. Under **Within-subjects Factor Name**, add the **Within-subjects Factors** in order. For each factor, enter the number of its conditions in **Number of Levels**.
   - The order of the factors must exactly match their order in your **User Data Excel file**. For example, if your column names follow the format `OneOfTheConditionInTheFirstFactor_OneOfTheConditionInTheSecondFactor_DependentVariable`, add `TheFirstFactor` first and `TheSecondFactor` second.

4. Under **Measure Name**, add **one** Dependent Variable.

5. Click **Define**.

6. Move the **Between-subjects factor(s)** required for the analysis into **Between-Subjects Factor(s)**.

7. Move the column names of the **Dependent Variable** required for the analysis into **Within-Subjects Variables**.
   - Check that the selected variables and their order are correct.

8. Click **Post Hoc**. Move all **Factor(s)** into **Post Hoc Tests for**, select **Tukey**, and click **Continue**.

9. Click **EM Means**. Move all **Factors and Factor Interactions**, except **(OVERALL)**, into **Display Means for**. Check both **Compare main effects** and **Compare simple main effects**. Under **Confidence interval adjustment**, select **Bonferroni**, then click **Continue**.

10. Click **Options**. Select **Descriptive statistics**, **Estimates of effect size**, and **Observed power**. Set the **Significance level** to **.05**, then click **Continue**.

11. Click **OK** to perform the analysis.

12. Export the analysis results. Please refer to the [**Export Analysis Results**](#export) section for instructions.

[back to toc](#table-of-contents)

### Univariate ANOVA

1. Open **IBM SPSS Statistics**, import your **User Data Excel file**, and select the sheet you want to use.

2. Select **Analyze > General Linear Model > Univariate**.

3. Move **one** Dependent Variable required for the analysis into **Dependent Variable**.

4. Move the **Between-subjects factor(s)** required for the analysis into **Fixed Factor(s)**.

5. Click **Post Hoc**. Move all **Between-subjects factor(s)** into **Post Hoc Tests for**, select **Tukey**, and click **Continue**.

6. Click **EM Means**. Move all **Factors and Factor Interactions**, except **(OVERALL)**, into **Display Means for**. Check both **Compare main effects** and **Compare simple main effects**. Under **Confidence interval adjustment**, select **Bonferroni**, then click **Continue**.

7. Click **Options**. Select **Descriptive statistics**, **Estimates of effect size**, **Observed power**, and **Homogeneity tests**. Set the **Significance level** to **.05**, then click **Continue**.

8. Click **OK** to perform the analysis.

9. Export the analysis results. Please refer to the [**Export Analysis Results**](#export) section for instructions.

[back to toc](#table-of-contents)

### Mann-Whitney U Test

1. Open **IBM SPSS Statistics**, import your **User Data Excel file**, and select the sheet you want to use.
   - The **Between-subjects factors** in the sheet must be converted to numeric values before performing the analysis. For example, if the `UserGender` factor contains two conditions, `Male` and `Female`, create a new column named `UserGenderGroup` and encode the conditions as `1` and `2`.

| UserGender | UserGenderGroup |
|------------|-----------------|
| Male       | 1               |
| Female     | 2               |
| Male       | 1               |
| Female     | 2               |

2. Select **Analyze > Nonparametric Tests > Legacy Dialogs > 2 Indenpendent Samples**.

3. Move one **numeric** Between-subjects factor required for the analysis into **Grouping Variable**.

4. Click **Define Groups** and enter the numeric values of the groups you want to compare in **Groups 1** and **Groups 2**, respectively, then click **Continue**.

5. Click **Options**. Under **Statistics**, select **Descriptive statistics**. Under **Missing Values**, select **Exclude cases test-by-test**, then click **Continue**.

6. Move the **Dependent Variable(s)** you want to analyze into **Test Variable List**. Multiple Dependent Variables can be selected at once. For example, if you are using the **Networked Mind Social Presence Inventory (NMSP)**, which contains six subscale scores, you can move all six Dependent Variables into **Test Variable List** at the same time.

7. Make sure **Mann-Whitney U** is selected under **Test Type**.

8. Click **OK** to perform the analysis.

9. Change the **Title** to a string that follows the required format:

   1. The string must be divided into **three parts** using the `-` symbol.
   2. The **first part** must be `MannWhitneyUTest`.
   3. The **second part** must contain the **Between-subjects factor name** followed by its numeric conditions.
   4. The **third part** must contain the numeric conditions and their corresponding condition names. Separate each numeric-condition pair using a comma (`,`).

   For example:
   `MannWhitneyUTest-UserGender12-1Male,2Female`

10. If you need to perform additional analyses on the **same Dependent Variables** using other **Between-subjects factors**, you can continue by selecting **Analyze > Nonparametric Tests > Legacy Dialogs > ...** to perform additional **nonparametric analyses (Mann-Whitney U Test or Kruskal-Wallis Test)**. This allows the results to be exported to the same Excel sheet.

   > **Note:** You should use the **Mann-Whitney U Test** only when the research design requires the Dependent Variables to be compared between **two groups** of the Between-subjects factor. If you need to compare **three or more groups**, please refer to the [**Kruskal-Wallis Test**](#kruskal-wallis-test) section.

11. Export the analysis results. Please refer to the [**Export Analysis Results**](#export) section for instructions.

[back to toc](#table-of-contents)

### Kruskal-Wallis Test

1. Open **IBM SPSS Statistics**, import your **User Data Excel file**, and select the sheet you want to use.
   - The **Between-subjects factors** in the sheet must be converted to numeric values before performing the analysis. For example, if the `TrainingMethod` factor contains two conditions, `MethodA`, `MethodB` and `MethodC`, create a new column named `TrainingMethodGroup` and encode the conditions as `1`, `2` and `3`.

| TrainingMethod | TrainingMethodGroup |
|----------------|---------------------|
| MethodA        | 1                   |
| MethodB        | 2                   |
| MethodC        | 3                   |
| MethodA        | 1                   |
| MethodC        | 3                   |
| MethodB        | 2                   |

2. Select **Analyze > Nonparametric Tests > Legacy Dialogs > K Indenpendent Samples**.

3. Move one **numeric** Between-subjects factor required for the analysis into **Grouping Variable**.

4. Click **Define Range** and enter the numeric value range of the groups you want to compare in **Minimum** and **Maximum**, then click **Continue**.

5. Click **Options**. Under **Statistics**, select **Descriptive statistics**. Under **Missing Values**, select **Exclude cases test-by-test**, then click **Continue**.

6. Move the **Dependent Variable(s)** you want to analyze into **Test Variable List**. Multiple Dependent Variables can be selected at once. For example, if you are using the **Networked Mind Social Presence Inventory (NMSP)**, which contains six subscale scores, you can move all six Dependent Variables into **Test Variable List** at the same time.

7. Make sure **Kruskal-Wallis H** is selected under **Test Type**.

8. Click **OK** to perform the analysis.

9. Change the **Title** to a string that follows the required format:

   1. The string must be divided into **three parts** using the `-` symbol.
   2. The **first part** must be `KruskalWallisHTest`.
   3. The **second part** must contain the **Between-subjects factor name** followed by its numeric conditions.
   4. The **third part** must contain the numeric conditions and their corresponding condition names. Separate each numeric-condition pair using a comma (`,`).

   For example:
   `KruskalWallisHTest-TrainingMethod123-1MethodA,2MethodB,3MethodC`

10. Please refer to the [**Mann-Whitney U Test**](#mann-whitney-u-test) section and perform a **Mann-Whitney U Test** for every pairwise combination of conditions. For example, if the current analysis is: `KruskalWallisHTest-TrainingMethod123-1MethodA,2MethodB,3MethodC`, you must also perform the following three pairwise comparisons (The order of the pairwise comparisons does not matter.):
    - `MannWhitneyUTest-TrainingMethod12-1MethodA,2MethodB`
    - `MannWhitneyUTest-TrainingMethod13-1MethodA,3MethodC`
    - `MannWhitneyUTest-TrainingMethod23-2MethodB,3MethodC`

11. If you need to perform additional analyses on the **same Dependent Variables** using other **Between-subjects factors**, you can continue by selecting **Analyze > Nonparametric Tests > Legacy Dialogs > ...** to perform additional **nonparametric analyses (Mann-Whitney U Test or Kruskal-Wallis Test)**. This allows the results to be exported to the same Excel sheet.

11. Export the analysis results. Please refer to the [**Export Analysis Results**](#export) section for instructions.

[back to toc](#table-of-contents)

### Export Analysis Results

After completing the analyses, export the results to an Excel file, with each analysis result exported to a separate sheet.

Please follow these requirements:

- **Use the same analysis method throughout the Excel file.** For example, if the first sheet contains the results of a **Repeated Measures ANOVA**, all other sheets in the same Excel file must also contain **Repeated Measures ANOVA** results.
- **For each individual sheet**, all results must be based on the **same Dependent Variable(s)**.
- For **Repeated Measures ANOVA** or **Univariate ANOVA**, make sure the hierarchy on the left contains **only one Output**.
- For **Nonparametric Tests** (**Mann-Whitney U Test** or **Kruskal-Wallis H Test**), a sheet may contain multiple **Outputs**. However, make sure that:
  - Every Output is a **Nonparametric Test** result.
  - All Outputs are based on the **same Dependent Variable(s)**.

#### Export Steps

1. Select **File > Export**.

2. Under **Objects to Export**, select **All visible**.

3. Under **Document Type**, select **Excel 2007 and Higher (*.xlsx)**.

4. In the **File Name** field, create a new Excel file or select the Excel file you used for the previous export.

5. Click **Change Options** and configure the following settings:
   - Under **What Do You Want to Do**, select **Create a worksheet**.
   - Under **Worksheet name**, enter a readable name that is preferably related to the **Dependent Variable**. The worksheet name must be **30 characters or fewer**.
   - Under **Location in Worksheet**, select **After last column**.
   - Under **Layers in Pivot Tables**, select **Honor Print Layer setting**.
   - Check **Include footnotes and captions**.
   - Under **Views of Models**, select **Honor Print Layer setting**.
   - Click **Continue**.

6. Optionally, check **Open the containing folder**. If selected, the folder containing the exported file will automatically open after the export is completed.

7. Click **OK** to export the results.

8. If you selected an existing Excel file, click **Yes** when prompted to confirm that you want to overwrite the file.

9. After each export, clear all **Output** contents from the hierarchy to prevent them from being accidentally included in the next export.

10. After exporting all required analysis results to the Excel file, open the file and **delete the empty worksheet that was initially created by Excel**.

[back to toc](#table-of-contents)

## Create a New Project in the System

After completing the **Factors.json**, **User Data Excel file**, and **SPSS Export Excel file**, you can create a new project in the system.

After the project is created, the system can help identify **statistically significant results** and provide functions for viewing **test statistics** and **descriptive statistics**.

### New Project Steps

Select **Project > New Project**.

On the **New Project** page, each page has a hint next to its title. Hover your mouse over the hint to view additional information. You can use the **`←`** and **`→`** arrow keys to navigate between pages, or press **`Enter`** to proceed to the next page.

1. **Project Name**  
   Enter the **Project Name**. The project name **cannot be changed after the project is created**, so please choose a name that clearly identifies the content of the project. There are **no restrictions on the length or format** of the project name.

2. **Factor Setting**  
   Select the **Factor Setting**. You can choose a Factor Setting that is already stored in the system, or import a new `Factor Setting JSON file` or create a new `Factor Setting`.

3. **User Data Excel File**  
   Select the **User Data Excel file**. You can choose a file that is already stored in the system, or import a new User Data Excel file.

4. **User Data Sheet(s)**  
   Select the **User Data Sheet(s)** that were used in your SPSS analyses, then click **Apply**.

   The system will validate whether your User Data meets the required format. If the validation fails, the problem may be caused by either the **Factor Setting** or the **User Data Excel file**. Please follow the displayed error messages to modify the relevant file, then import and select the corrected files again.

   If the validation is successful, the system will display the **Dependent Variables** identified from your User Data Excel file and group them into categories based on their **sheet names**. You can modify the category names to improve the readability of the **significant results** that will be exported later.

   For each Dependent Variable:

   - If you did not perform an analysis on a particular Dependent Variable, click the **eye button** to hide it.
   - If you performed multiple analyses on a particular Dependent Variable and it corresponds to multiple sheets in the **SPSS Export Excel file**, change the **number of sheets** for that Dependent Variable accordingly.
   - Make sure that the multiple sheets corresponding to the same Dependent Variable in the **SPSS Export Excel file** are arranged **consecutively without being separated by sheets for other Dependent Variables**.

5. **SPSS Export Excel File**  
   Select the **SPSS Export Excel File** that contains the results of the SPSS analyses performed using the currently selected **User Data Excel file**.

6. **Validate Analysis Method**

   1. Since the **Sheet names** in the SPSS Export Excel File and the **Dependent Variables** in the User Data Excel File are named by you, the system cannot automatically determine whether they correspond correctly. Therefore, please check that all **SPSS Export Excel File Sheet names** are correctly matched to the corresponding **Dependent Variables** in the User Data Excel File.
      
      - If the number of sheets and Dependent Variables does not match, return to **Step 4** and adjust the **number of sheets** setting for the corresponding Dependent Variables.
      
      - If the order does not match, rearrange the sheets in the **SPSS Export Excel File**, then return to **Step 5** and import and select the file again.

   2. The **Analysis Method** column on the far right displays the analysis methods identified by the system from your SPSS Export Excel File.
      
      Please make sure that your SPSS Export Excel File was created according to the procedures described in the [**Perform SPSS Analysis**](#perform-spss-analysis) section so that the analysis methods can be correctly identified.
      
      - If an analysis method is not correctly identified, please check whether the SPSS analysis and export procedures were followed correctly.
      
      The system requires **all sheets in the same Excel file to use the same Analysis Method**. If the SPSS Export Excel File contains multiple Analysis Methods, the validation will fail.

   3. After the validation is successful, click **Done** to create the new project.

[back to toc](#table-of-contents)

## Export Significant Results

After creating a new project, you can access your projects through **Project > Open Recent**. Each project provides two functions: **Export Significant Results** and **Query Analysis Details**.

**Export Significant Results** automatically checks all analysis results in the **SPSS Export Excel File** for significant results and exports them to an Excel file.

Effects with a **significance value (p-value) < 0.05** are classified as **significant results**. Effects with a **significance value (p-value) >= 0.05 and < 0.1** are classified as **potential results**.

### Repeated Measures ANOVA and Univariate ANOVA

For **Repeated Measures ANOVA** and **Univariate ANOVA**, the exported table contains the following columns:

- **Category**
- **Dependent Variable**
- **Factor**
- **Homogeneous**
- **Effect**
- **Result**

The information in these columns is determined as follows:

- **Category**: The category name you assigned in **Step 4** when creating the New Project.
- **Dependent Variable**: The Dependent Variable name from your **User Data Excel File**.
- **Factor**: The Factor(s) used in the corresponding SPSS Export Excel File sheet.
- **Homogeneous**: Displays the assumption tests that were not passed in the analysis:
  - **Mauchly's Test of Sphericity** for **Repeated Measures ANOVA**.
  - **Levene's Test of Equality of Error Variances** for **Univariate ANOVA**.
- **Effect**: Displays the significant results identified from the **Tests of Between-Subjects Effects** and **Tests of Within-Subjects Effects** tables in the SPSS Export Excel File.
- **Result**: Displays the significant results from the **Pairwise Comparisons** corresponding to each Effect.

[back to toc](#table-of-contents)

### Nonparametric Tests (Mann-Whitney U Test or Kruskal-Wallis H Test)

For **Mann-Whitney U Test** or **Kruskal-Wallis H Test**, the exported table contains the following columns:

- **Category**
- **Dependent Variable**
- **Effect**
- **Result**

The information in these columns is determined as follows:

- **Category**: The **SPSS Export Excel File Sheet name** used for the corresponding analysis.
- **Dependent Variable**: The Dependent Variable(s) used in the corresponding analysis.
- **Effect**: Displays the significant results identified from the **Test Statistics** table in the SPSS Export Excel File.
- **Result**: Determines the direction of each Effect based on the **Ranks** table.

If a Dependent Variable is analyzed using the **Kruskal-Wallis H Test**, the system first identifies the significant Effect from the **Test Statistics** table of the Kruskal-Wallis H Test. It then examines the corresponding pairwise **Mann-Whitney U Tests**:

1. Check the **Test Statistics** table for each pairwise Mann-Whitney U Test.
2. Apply **Bonferroni correction** by multiplying the significance value (p-value) by **3**. The pairwise comparison is considered significant only if the corrected p-value remains significant.
3. For significant pairwise comparisons, check the **Ranks** table to determine the direction of the Effect.

[back to toc](#table-of-contents)

## Query Analysis Details

After creating a new project, you can access your projects through **Project > Open Recent**. Each project provides two functions: **Export Significant Results** and **Query Analysis Details**.

**Query Analysis Details** 可以協助您查詢 the **SPSS Export Excel File** 中的 Test Statistics 以及 Descriptive Statistics。

### Test Statistics

**Test Statistics** provides the statistical test results used to determine whether there is a statistically significant difference or effect in the analysis.

The following statistics are commonly used to interpret the results:

- **df**: Degrees of freedom.
- **Sig.**: The significance value (**p-value**), which indicates whether the result is statistically significant.
- **$\eta_p^2$ (Partial Eta Squared)**: An effect size used in ANOVA to indicate the proportion of variance in the Dependent Variable that is associated with a specific Effect, after accounting for other effects in the model. A larger $\eta_p^2$ indicates a larger effect.
- **$\eta_H^2$ (Eta Squared for Kruskal-Wallis H Test)**: An effect size used with the Kruskal-Wallis H Test to indicate the magnitude of the differences among groups. A larger $\eta_H^2$ indicates a larger effect.
- **$r$**: An effect size commonly used for the Mann-Whitney U Test to indicate the magnitude of the difference between two groups. The absolute value of $r$ indicates the effect size, while the sign can indicate the direction of the effect when calculated from the corresponding standardized test statistic.
- **$\chi^2$ (Chi-Square)**: A test statistic used in tests such as Mauchly's Test of Sphericity and the Kruskal-Wallis H Test. It is used, together with its degrees of freedom, to calculate the corresponding significance value (**p-value**).

Depending on the analysis method, the table may contain different statistics, such as:

* **F**: The test statistic used in ANOVA. (e.g. $F(2, 69) = 4.32, p = .017, \eta_p^2 = .111$)
* **Kruskal-Wallis H**: The test statistic used in the Kruskal-Wallis H Test. (e.g. $H(2) = 8.64, p = .013, \eta_H^2 = .092$)
* **Mann-Whitney U**: The test statistic used in the Mann-Whitney U Test. (e.g. $U = 125.00, p = .032, r = .34$)
* **Mauchly's W**: The test statistic used in Mauchly's Test of Sphericity. (e.g. $W = .823, \chi^2(2) = 12.45, p = .002$)
* **Levene's Test**: The test used to assess the homogeneity of error variances in Univariate ANOVA. (e.g. $F(2, 69) = 3.21, p = .046$)

[back to toc](#table-of-contents)

### Descriptive Statistics

**Descriptive Statistics** provides a summary of the observed data and helps you understand the characteristics of each group or condition.

Depending on the analysis, the table may contain information such as:

- **N**: The number of observations or participants.
- **Mean (M)**: The average value of the observed data.
- **Standard Deviation (SD)**: The amount of variation or dispersion in the data around the mean.
- **Median (Mdn)**: The middle value of the observed data when the values are arranged in ascending order.
- **Interquartile Range (IQR)**: The range between the 25th percentile (Q1) and the 75th percentile (Q3), representing the middle 50% of the observed data.

Descriptive Statistics should be used together with **Test Statistics**. While Test Statistics determines whether an effect or difference is statistically significant, Descriptive Statistics helps you understand the actual values and direction of the observed differences.

For **ANOVA** results, use **Mean (M)** and **Standard Deviation (SD)** for each group or condition to interpret the observed differences. For **Nonparametric Tests** results, use **Median (Mdn)** and **Interquartile Range (IQR)** for each group or condition to interpret the observed differences.

[back to toc](#table-of-contents)

## Data Management

You can manage **Factor, User Data, and SPSS Export** files through the **Data** menu. You can also manage your Projects through **Project > Open Recent**.

All stored data can be downloaded to your preferred location at any time.

### Editing Factor Data

Under **Data > Factor**, Factor data can be modified by clicking the **orange pencil button** in the corresponding data row.

### Deleting Data

You can delete an individual item by clicking the **red trash can button** in its data row. To delete multiple items at once, click the **Select** button to enter selection mode and choose the data you want to delete.

> ⚠️ **Warning:** Deleted data cannot be recovered. Please make sure that the data is no longer needed before deleting it.

If the deletion prompt is displayed in a **warning color**, it indicates that one or more Projects currently depend on the selected data. Deleting the data will also cause the **related Projects to be deleted**.

Please carefully review the warning message and confirm that the data and its dependent Projects are no longer needed before proceeding with the deletion.

[back to toc](#table-of-contents)