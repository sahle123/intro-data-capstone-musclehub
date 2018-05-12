
# coding: utf-8

# # Capstone Project 1: MuscleHub AB Test

# ## Step 1: Get started with SQL

# Like most businesses, Janet keeps her data in a SQL database.  Normally, you'd download the data from her database to a csv file, and then load it into a Jupyter Notebook using Pandas.
# 
# For this project, you'll have to access SQL in a slightly different way.  You'll be using a special Codecademy library that lets you type SQL queries directly into this Jupyter notebook.  You'll have pass each SQL query as an argument to a function called `sql_query`.  Each query will return a Pandas DataFrame.  Here's an example:

# In[1]:


# This import only needs to happen once, at the beginning of the notebook
from codecademySQL import sql_query


# In[2]:


# Here's an example of a query that just displays some data
sql_query('''
SELECT *
FROM visits
LIMIT 5
''')


# In[3]:


# Here's an example where we save the data to a DataFrame
df = sql_query('''
SELECT *
FROM applications
limit 10
''')

#len(df['index'])
df.head(10)


# ## Step 2: Get your dataset

# Let's get started!
# 
# Janet of MuscleHub has a SQLite database, which contains several tables that will be helpful to you in this investigation:
# - `visits` contains information about potential gym customers who have visited MuscleHub
# - `fitness_tests` contains information about potential customers in "Group A", who were given a fitness test
# - `applications` contains information about any potential customers (both "Group A" and "Group B") who filled out an application.  Not everyone in `visits` will have filled out an application.
# - `purchases` contains information about customers who purchased a membership to MuscleHub.
# 
# Use the space below to examine each table.

# In[4]:


# Examine visits here
df_visits = sql_query('''
SELECT *
FROM visits
LIMIT 5
''')

df_visits


# In[5]:


# Examine fitness_tests here
df_fitness_tests = sql_query('''
select * from fitness_tests
limit 5
''')

df_fitness_tests


# In[6]:


# Examine applications here
df_appl = sql_query('''
select * from applications
limit 5
''')

df_appl


# In[7]:


# Examine purchases here
df_purchases = sql_query('''
select * from purchases
limit 5
''')

df_purchases


# We'd like to download a giant DataFrame containing all of this data.  You'll need to write a query that does the following things:
# 
# 1. Not all visits in  `visits` occurred during the A/B test.  You'll only want to pull data where `visit_date` is on or after `7-1-17`.
# 
# 2. You'll want to perform a series of `LEFT JOIN` commands to combine the four tables that we care about.  You'll need to perform the joins on `first_name`, `last_name`, and `email`.  Pull the following columns:
# 
# 
# - `visits.first_name`
# - `visits.last_name`
# - `visits.gender`
# - `visits.email`
# - `visits.visit_date`
# - `fitness_tests.fitness_test_date`
# - `applications.application_date`
# - `purchases.purchase_date`
# 
# Save the result of this query to a variable called `df`.
# 
# Hint: your result should have 5004 rows.  Does it?

# In[8]:


df = sql_query('''
SELECT
    v.first_name,
    v.last_name,
    v.gender,
    v.email,
    v.visit_date,
    ft.fitness_test_date,
    app.application_date,
    p.purchase_date
FROM visits AS v
LEFT JOIN fitness_tests AS ft ON
    v.first_name = ft.first_name AND
    v.last_name = ft.last_name AND
    v.email = ft.email
LEFT JOIN applications AS app ON
    v.first_name = app.first_name AND
    v.last_name = app.last_name AND
    v.email = app.email
LEFT JOIN purchases AS p ON
    v.first_name = p.first_name AND
    v.last_name = p.last_name AND
    v.email = p.email

WHERE v.visit_date >= '7-1-17'
''')

df.head(12)


# ## Step 3: Investigate the A and B groups

# We have some data to work with! Import the following modules so that we can start doing analysis:
# - `import pandas as pd`
# - `from matplotlib import pyplot as plt`

# In[9]:


import pandas as pd
from matplotlib import pyplot as plt


# We're going to add some columns to `df` to help us with our analysis.
# 
# Start by adding a column called `ab_test_group`.  It should be `A` if `fitness_test_date` is not `None`, and `B` if `fitness_test_date` is `None`.

# In[10]:


ab_lambda = lambda x: "B" if (x["fitness_test_date"] is None) else "A"
df["ab_test_group"] = df.apply(ab_lambda, axis=1)

#df[df["fitness_test_date"].isnull()].head(25)
#df[df["fitness_test_date"].notnull()].head(25)
#df[(df["application_date"].notnull())&(df["ab_test_group"]=="B")].head()


# Let's do a quick sanity check that Janet split her visitors such that about half are in A and half are in B.
# 
# Start by using `groupby` to count how many users are in each `ab_test_group`.  Save the results to `ab_counts`.

# In[11]:


df_ab_groups = df.groupby("ab_test_group")["email"].count().reset_index()
df_ab_groups.rename(columns={"email":"Participants"}, inplace=True)
df_ab_groups


# We'll want to include this information in our presentation.  Let's create a pie cart using `plt.pie`.  Make sure to include:
# - Use `plt.axis('equal')` so that your pie chart looks nice
# - Add a legend labeling `A` and `B`
# - Use `autopct` to label the percentage of each group
# - Save your figure as `ab_test_pie_chart.png`

# In[12]:


a = df_ab_groups["Participants"].tolist()
l = ["A", "B"]

plt.pie(a, labels=l, autopct="%0.5f%%", colors=['#ddf5f5', '#dd7777'])
plt.legend(["Group A", "Group B"])
plt.axis("equal")
plt.title("Participant distribution", y=1.09)

plt.savefig("ab_test_pie_chart.png")

plt.show()


# ## Step 4: Who picks up an application?

# Recall that the sign-up process for MuscleHub has several steps:
# 1. Take a fitness test with a personal trainer (only Group A)
# 2. Fill out an application for the gym
# 3. Send in their payment for their first month's membership
# 
# Let's examine how many people make it to Step 2, filling out an application.
# 
# Start by creating a new column in `df` called `is_application` which is `Application` if `application_date` is not `None` and `No Application`, otherwise.

# In[13]:


df["is_application"] = df.apply(lambda x: "No Application" if (x["application_date"] is None) else "Application", axis=1)

#df.groupby("is_application")["first_name"].count().reset_index().rename(columns={"first_name":"Count"})
df.head(10)
#df[(df["ab_test_group"] == "B") & (df["is_application"] == "No Application")].count()


# Now, using `groupby`, count how many people from Group A and Group B either do or don't pick up an application.  You'll want to group by `ab_test_group` and `is_application`.  Save this new DataFrame as `app_counts`

# In[14]:


app_counts = df.groupby(["ab_test_group", "is_application"])["first_name"].count().reset_index()                            .rename(columns={"first_name":"Count"})
app_counts


# We're going to want to calculate the percent of people in each group who complete an application.  It's going to be much easier to do this if we pivot `app_counts` such that:
# - The `index` is `ab_test_group`
# - The `columns` are `is_application`
# Perform this pivot and save it to the variable `app_pivot`.  Remember to call `reset_index()` at the end of the pivot!

# In[15]:


app_pivot = app_counts.pivot(index="ab_test_group", columns="is_application", values="Count").reset_index()
#app_counts = app_counts.rename(columns={"is_application":"id"})
app_pivot


# Define a new column called `Total`, which is the sum of `Application` and `No Application`.

# In[16]:


app_pivot["Total"] = app_pivot.apply(lambda x: x["Application"] + x["No Application"], axis=1)
app_pivot


# Calculate another column called `Percent with Application`, which is equal to `Application` divided by `Total`.

# In[17]:


app_pivot["Percent with Application"] = app_pivot.apply(lambda x: float(x["Application"])/float(x["Total"]), axis=1)
app_pivot


# It looks like more people from Group B turned in an application.  Why might that be?
# 
# We need to know if this difference is statistically significant.
# 
# Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[18]:


from scipy.stats import binom_test

b_success = app_pivot[app_pivot["ab_test_group"] == "B"]["Application"].iloc[0]
b_sample_size = app_pivot[app_pivot["ab_test_group"] == "B"]["Total"].iloc[0]
a_percent = app_pivot[app_pivot["ab_test_group"] == "A"]["Percent with Application"].iloc[0]

# Using number of signs in B, B sample size, expected percentage of signs of group A.
pval_B = binom_test(x=b_success, n=b_sample_size, p=a_percent)
print "P-value of B: " + str(pval_B)
print "It appears we can reject the null hypothesis. The groups are different."


# ## Step 4: Who purchases a membership?

# Of those who picked up an application, how many purchased a membership?
# 
# Let's begin by adding a column to `df` called `is_member` which is `Member` if `purchase_date` is not `None`, and `Not Member` otherwise.

# In[19]:


df["is_member"] = df.apply(lambda x: "Member" if x["purchase_date"] is not None else "Not Member", axis=1)

cols = ["first_name", "last_name", "fitness_test_date", "application_date", "purchase_date", "ab_test_group", "is_application", "is_member"]
#df.loc[:, cols].head(20)


# Now, let's create a DataFrame called `just_apps` the contains only people who picked up an application.

# In[20]:


just_apps = df[(df["is_application"] == "Application")]
just_apps.loc[:, cols].head(5)


# Great! Now, let's do a `groupby` to find out how many people in `just_apps` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `member_pivot`.

# In[21]:


member_pivot          = just_apps.groupby(["ab_test_group", "is_member"])["first_name"].count().reset_index()
member_pivot.rename(columns={"first_name": "Count"}, inplace=True)

member_pivot          = member_pivot.pivot(index="ab_test_group", columns="is_member", values="Count").reset_index()
member_pivot["Total"] = member_pivot.apply(lambda x: x["Member"] + x["Not Member"], axis=1)

member_pivot["Percent Purchase"] = member_pivot.apply(lambda x: float(x["Member"])/float(x["Total"]), axis=1)

member_pivot


# It looks like people who took the fitness test were more likely to purchase a membership **if** they picked up an application.  Why might that be?
# 
# Just like before, we need to know if this difference is statistically significant.  Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[22]:


from scipy.stats import binom_test

b_success     = member_pivot[member_pivot["ab_test_group"] == "B"]["Member"].iloc[0]
b_sample_size = member_pivot[member_pivot["ab_test_group"] == "B"]["Total"].iloc[0]
a_percent     = member_pivot[member_pivot["ab_test_group"] == "A"]["Percent Purchase"].iloc[0]

pval_B = binom_test(x=b_success, n=b_sample_size, p=a_percent)

print pval_B
print "We cannot reject the null hypothesis. P-value is too large"


# Previously, we looked at what percent of people **who picked up applications** purchased memberships.  What we really care about is what percentage of **all visitors** purchased memberships.  Return to `df` and do a `groupby` to find out how many people in `df` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `final_member_pivot`.

# In[23]:


final_member_pivot = df.groupby(["ab_test_group", "is_member"])["first_name"].count().reset_index()                       .rename(columns={"first_name": "Count"})
    
final_member_pivot = final_member_pivot.pivot(index="ab_test_group", columns="is_member", values="Count").reset_index()

final_member_pivot["Total"] = final_member_pivot.apply(lambda x: x["Member"] + x["Not Member"], axis=1)
final_member_pivot["Percent Purchase"] = final_member_pivot.apply(lambda x: float(x["Member"])/float(x["Total"]), axis=1)

final_member_pivot


# Previously, when we only considered people who had **already picked up an application**, we saw that there was no significant difference in membership between Group A and Group B.
# 
# Now, when we consider all people who **visit MuscleHub**, we see that there might be a significant difference in memberships between Group A and Group B.  Perform a significance test and check.

# In[24]:


from scipy.stats import chi2_contingency, binom_test

pval_B = binom_test(x=250, n=2500, p=0.079872)
_, pval_B2, _, _ = chi2_contingency([[200, 2304], [250, 2250]])

print pval_B
print pval_B2

print "Both the binomial test and chi-squared tests have low enough p-values to reject the null hypothesis. There is a difference between both groups"


# ## Step 5: Summarize the acquisition funel with a chart

# We'd like to make a bar chart for Janet that shows the difference between Group A (people who were given the fitness test) and Group B (people who were not given the fitness test) at each state of the process:
# - Percent of visitors who apply
# - Percent of applicants who purchase a membership
# - Percent of visitors who purchase a membership
# 
# Create one plot for **each** of the three sets of percentages that you calculated in `app_pivot`, `member_pivot` and `final_member_pivot`.  Each plot should:
# - Label the two bars as `Fitness Test` and `No Fitness Test`
# - Make sure that the y-axis ticks are expressed as percents (i.e., `5%`)
# - Have a title

# In[25]:


from matplotlib import pyplot as plt

# app_pivot graphs
application_numbers = app_pivot["Percent with Application"].tolist()

ax = plt.subplot()

plt.bar(range(len(app_pivot)), application_numbers)

ax.set_xticks(range(len(app_pivot)))
ax.set_xticklabels(["Fitness Test", "No Fitness Test"])
ax.set_yticks([0.0, 0.05, 0.10, 0.15, 0.20])
ax.set_yticklabels(["0%", "5%", "10%", "15%", "20%"])

plt.ylabel("Percent of application sign-ups")
plt.xlabel("Groups")
plt.title("Visitors filling out applications")

plt.savefig("application_signups_by_group.png")
plt.show()


# In[26]:


# member_pivot graphs

application_numbers = member_pivot["Percent Purchase"].tolist()

ax = plt.subplot()
plt.bar(range(len(member_pivot)), application_numbers)

# X
ax.set_xticks(range(len(member_pivot)))
ax.set_xticklabels(["Fitness Test", "No Fitness Test"])

# Y
y_range = [ float(i) / 100 for i in range(70, 95, 5)]
ax.set_yticks(y_range)
ax.set_yticklabels(["70%", "75%", "80%", "85%", "90%"])
plt.ylim([0.65, 0.90]) # Adjust y-limits

plt.ylabel("Percent of members signed up")
plt.xlabel("Groups")
plt.title("Applicants signing up for membership")

plt.savefig("membership_signups_by_group.png")
plt.show()


# In[27]:


# final_member_pivot
application_numbers = final_member_pivot["Percent Purchase"].tolist()

ax = plt.subplot()

plt.bar(range(len(final_member_pivot)), application_numbers)

# X
ax.set_xticks(range(len(final_member_pivot)))
ax.set_xticklabels(["Fitness Test", "No Fitness Test"])

# Y
ax.set_yticks([float(i)/100 for i in range(0, 14, 2)])
ax.set_yticklabels(["0%", "2%", "4%", "6%", "8%", "10%", "12%"])

plt.ylabel("Percent of application sign-ups")
plt.xlabel("Groups")
plt.title("Vistors signing up for a membership")

plt.savefig("visitor_membership_signup.png")
plt.show()

