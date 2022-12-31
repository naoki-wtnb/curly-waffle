# Start with the necessary imports.
import pandas as pd
import matplotlib.pyplot as plt

pd.options.mode.chained_assignment = None

# The input files are specified as global variables.

spending_report = 'amazon_spending.csv'
refund_report = 'amazon_refund.csv'
discard_list_txt = 'discard_strings.txt'

def get_list_from_strings_txt(filename):
    # opening the file in read mode
    my_file = open(filename, "r")
  
    # reading the file
    data = my_file.read()
  
    # replacing end splitting the text 
    # when newline ('\n') is seen.
    discard_list = data.split("\n")
    my_file.close()
    return discard_list

def create_dataframe_from_csv(spending_csv, refund_csv):
    
  

    # create a dataframe called df1 by reading an Amazon spending csv file.
    df1 = pd.read_csv(spending_csv)

    # create dataframe called df2 by reading an Amazon return csv file.
    df2 = pd.read_csv(refund_csv)
    
   #clean
    df1["Item Total"] = df1["Item Total"].str.replace(r'\$','', regex=True).astype(float)
    df2["Refund Amount"] = df2["Refund Amount"].str.replace(r'\$','', regex=True).astype(float)
    df2["Refund Tax Amount"] = df2["Refund Tax Amount"].str.replace(r'\$','', regex=True).astype(float)

    # NaN is replaced with 0.
    df1 = df1.fillna(0)
    df2 = df2.fillna(0)
    # remove rows that has a value "Return Processing Error" in the column "Refund Reason".
    df2 = df2.loc[df2["Refund Reason"] != 'Return Processing Error']

    # aggregrate duplicates in df2 and sum the 'Refund Amount' and 'Refund Tax Amount'.
    
   # From df2 create a subset dataframe called return_sumbsets with three columns that I am interested.
    return_subset = df2[["Order ID", "Title", "Refund Condition", "Refund Amount", "Refund Tax Amount"]]
    
    #define how to aggregate various fields
    agg_functions = {'Refund Condition': 'first', 'Refund Amount': 'sum', 'Refund Tax Amount': 'sum'}


    #print(return_subset.info())
    #create new return_subset by combining rows with same id values
    return_subset = return_subset.groupby(['Order ID','Title']).aggregate(agg_functions)
    
    # merge the return_subset to df1 using the "Order ID" as the key
     
    df = pd.merge(df1, return_subset, how = 'left', on = ["Order ID", "Title"])
    df = df.fillna(0)
    
    
    return df


#def clean_dataframe(df):
    
    
    # remove the "$" sign and change the type from string to float.
    # r'\D','', regex=True - replaces anything other than digit to nothing. regex=True is necesary because in the future version the default would be regex=False
   # df["Item Total"] = df["Item Total"].str.replace(r'\$','', regex=True).astype(float)
    #df["Refund Amount"] = df["Refund Amount"].str.replace(r'\$','', regex=True).astype(float)
    #df["Refund Tax Amount"] = df["Refund Tax Amount"].str.replace(r'\$','', regex=True).astype(float)

    # NaN is replaced with 0.
    #df = df.fillna(0)
   
    #return df

def discard_rows_certain_strings(df, discard_list):
    
    
    #dropping items in the discard_list
    for i in discard_list:
        df = df[df["Title"].str.contains(i, case=False) == False]
   
    return df    

def add_spendingtotal_refundtotal_column(df):
    
    
    # Create a new column called "Refund Total" by adding "Refund Amount" and "Refund Tax Amount".
    df["Refund Total"] = df["Refund Amount"] + df["Refund Tax Amount"]

    # Create a new column called "Spending Total" by subtracting "Refund Total" from "Item Total"
    df["Spending Total"] = df["Item Total"] - df["Refund Total"]
    
    
    return df
 
def sum_spending_total(df):
    
    # sum all the values in the "Spending Total" column.
    sum_spending = df["Spending Total"].sum()
    #print("Your total Amazon spending is $", sum_spending.astype(int))
    return sum_spending

def sum_refund_total(df):
    
    # sum all the values in the "Refund Total" column.
    sum_refund = df["Refund Total"].sum()
    #print("Your total Amazon refund is $", sum_refund.astype(int))
    return sum_refund

def create_refund_total_subset(df):
    
    df = df[["Order Date","Title", "Refund Total"]]
     # remove rows without titles
    df = df.loc[df["Refund Total"] != 0]
    df = df.sort_values(by = ['Refund Total','Order Date', 'Title'], ascending=[False, True, True])
    return df

def create_refund_total_html(df):

    df.to_html('refund_total_table.html', header=True, index=False)
    
    return

def create_month_year_column(df):
    
    
    #Transforming the type to datetime
    df["Order Date"] = pd.to_datetime(df["Order Date"])

    #Extracting year into a new column "year", month into a new column"month".
    df["year"] = df["Order Date"].dt.year
    df["month"] = df["Order Date"].dt.month
    
    return df

   
def create_refundtotal_spendingtotal_month_year_subset(df):
    
    
    # create a subset dataframe called df with 4 column, "Refund Total", "Spending Total", "month" and "year".

    df = df[["Refund Total", "Spending Total", "month", "year"]]
    
    
    
    return df



def create_df_group_by_year(df):
    
    # group "Spending Total" by year.

    yearly_spending = df.groupby("year").sum(numeric_only= True)["Spending Total"]

    # group "Refund Total" by year.

    yearly_refund = df.groupby("year").sum(numeric_only= True)["Refund Total"]

    # create a dataframe by combining two Series, yearly_refund and yearly_spending.

    pd.concat([yearly_spending, yearly_refund], axis=1)


    # assigned it to a variable df.

    df = pd.concat([yearly_spending, yearly_refund], axis=1)

    #print(df)
    return df


def create_df_group_by_month(df):
    
    
    # group "Spending Total" by month.

    monthly_spending = df.groupby("month").mean(numeric_only= True)["Spending Total"]
    

    # group "Refund Total" by month.

    monthly_refund = df.groupby("month").mean(numeric_only= True)["Refund Total"]

    # create a dataframe by combining two Series, monthly_refund and monthly_spending.

    pd.concat([monthly_refund, monthly_spending], axis=1)


    # assigned it to a variable df.

    df = pd.concat([monthly_spending, monthly_refund], axis=1)
    
   

    #print(df)
    return df

#def create_df_with_monthly_avg(df):
    
     #add average monthly spending column
    #df["avg monthly spending"] = df["monthly_spending"] / 12
    #df["avg monthly refund"] = df["monthly_refund"] / 12
    #df = df[["avg monthly spending", "avg monthly refund"]]
    #return df

def create_save_graph_monthly_avg(df):


    # create a stacked bar graph, and make a title.

    df.plot.bar(stacked = True, title = 'Amazon AVG Monthly Spending vs. Refund')

    plt.savefig('plot_monthly_avg.png')

    graph = 'plot_monthly_avg.png'
    
    return graph
def create_save_graph_yearly(df):


    # create a stacked bar graph, and make a title.

    df.plot.bar(stacked = True, title = 'Amazon Yearly Spending vs. Refund')

    plt.savefig('plot_yearly.png')

    graph = 'plot_yearly.png'
    
    return graph


#def create_save_graph_monthly(df):


    # create a stacked bar graph, and make a title.

    #df.plot.bar(stacked = True, title = 'Amazon Monthly Spending vs. Refund')

    #plt.savefig('plot_monthly.png')

    #graph = 'plot_monthly.png'
    
    #return graph


def create_date_title_category_spendingtotal_refundtotal_subset(df):
    
    
    # create a subset dataframe with 4 column, "Order Date", "Title","Category", "Item Total".

    df = df[["Order Date", "Title","Category", "Item Total"]]
    
    return df


def create_books_subset(df):
    
    # create a subset dataframe with a value "ABIS_BOOK" in the Category column.
    
    df_books_subset=df.query("Category == 'ABIS_BOOK'")

    # drop the index
    df_books_subset = df_books_subset.drop('Category', axis =1)
    
    return df_books_subset


def render_df_as_bookshtml(df):
   

    df.to_html('books.html', header=True, index=False)
    
    return 


def remove_return_complete(df):
    
    # create subset dataframe with column value that is not return completed.
    df = df.loc[df["Refund Condition"] != 'Completed']
    
    # remove rows without titles
    df = df.loc[df["Title"] != 0]
    
    return df

def create_orderdate_title_itemtotal_df(df):

    df = df[['Order Date', 'Title','Item Total']]
    
    return df


def find_duplicate(df):
    
    df_duplicate = df[df.duplicated('Title')]
   
    df_duplicate = df_duplicate.sort_values(by = ['Title','Order Date'], ascending=[True, True])
    
    return df_duplicate


    
def render_df_as_duplicatehtml(df):
   

    df.to_html('duplicate.html', header=True, index=False)
    
    return

def create_year_column(df):
    #print (df["Order Date"])
    
    #Transforming the type to datetime
    #df["Order Date"] = pd.to_datetime(df["Order Date"]) #<- this one got warning
    #df.loc[:,"Order Date"] = pd.to_datetime(df.loc[:,"Order Date"])

    
    #Extracting year into a new column "year".
    df["year"] = df["Order Date"].dt.year # <- this one got warning
    #df.loc[:,"year"] = df.loc[:,"Order Date"].dt.year
    
    return df
   

def sort_by_year_itemtotal(df):
    df = df.sort_values(by = ['year', 'Item Total'], ascending=[True, False])
    
    return df

def get_top10_eachyear(df):
    
    df = df.groupby('year').head(10).reset_index(drop=True)
    df = df[['Title','Item Total','year']]
    
    
    
    return df

def render_df_as_top10html(df):
   
   
    df.to_html('top10.html', header=True, index=False)
    
    return

def create_html(filename):
    # Creating the HTML file
    file_html = open(filename, "w")

    # Adding the input data to the HTML file
    file_html.write('''<!DOCTYPE html>
<html>

<head>

<link rel="stylesheet" type="text/css" href="df_style.css"/>
<style>

    @page {
    margin:.25in;
    padding:0;
    }

    @media print {
    html, body {
    width:110%;
    height:auto;
    margin:auto;
    padding:0;
    }

    #main_container { left:-278px !important; }
    #playbar { display:none !important; }
    [id^="Button_"]{ display:none !important;}
}
h1{text-align: center;}
h2 {text-align: center;}
h3 {text-align: center;}
p {text-align: center;}
div {text-align: center;}
</style>

<title>Result</title>

</head>



<body>
  <h1>Amazon Spending & Refund Report</h1>
  
  
  <br>
  
  <center>
  <img src= 'plot_yearly.png' >
  <img src= 'plot_monthly_avg.png'>
  </center>
<br>
    <h2>Books Purchased (<a href="books.html" target="_blank">Full Table</a>)</h2>
   <div>
    
    <iframe src="books.html" width="70%" height="100%" style="border:none;">
</iframe>
    </div>
<br>
    <h2>Duplicate Purchases (<a href="duplicate.html" target="_blank">Full Table</a>)</h2>
       <div>
        
        <iframe src="duplicate.html" width="70%" height="100%" style="border:none;">
    </iframe></div>
    
<br>
    <h2>10 Most Expensive Purchases by Year (<a href="top10.html" target="_blank">Full Table</a>)</h2>
       <div>
        
        <iframe src="top10.html" width="70%" height="100%" style="border:none;">
    </iframe></div>
             
<br>


<br>

</body>

</html>''')

    # Saving the data into the HTML file
    file_html.close()
 
def open_localfile(filename):
    import webbrowser, os
    webbrowser.open('file://' + os.path.realpath(filename))
     
     
def main():
    
    try:
        discard_list = get_list_from_strings_txt(discard_list_txt)
    
    except:
        pass
    
    output_filename = "result.html"
    df_cleaned = create_dataframe_from_csv(spending_report, refund_report)
    
    
    #df_cleaned = clean_dataframe(df_raw)
    try:
        df_cleaned = discard_rows_certain_strings(df_cleaned, discard_list)
    except:
        pass
    
    df_columnmerged = add_spendingtotal_refundtotal_column(df_cleaned)
    sum_spending = sum_spending_total(df_columnmerged)
    sum_refund = sum_refund_total(df_columnmerged)
    df_refund_total_subset = create_refund_total_subset(df_columnmerged)
    create_refund_total_html(df_refund_total_subset)
    df_with_month_year = create_month_year_column(df_columnmerged)
    df_subset = create_refundtotal_spendingtotal_month_year_subset(df_with_month_year)
    df_by_year = create_df_group_by_year(df_subset)
    df_by_month = create_df_group_by_month(df_subset)
    #df_with_monthly_avg = create_df_with_monthly_avg(df_by_month)
    create_save_graph_yearly(df_by_year)
    #create_save_graph_monthly(df_with_monthly_avg)
    create_save_graph_monthly_avg(df_by_month)
    df_title_category = create_date_title_category_spendingtotal_refundtotal_subset(df_with_month_year)
    df_books = create_books_subset(df_title_category)
    render_df_as_bookshtml(df_books)
    df_return_complete_removed = remove_return_complete(df_cleaned)
    df_date_title_itmeorder_subset = create_orderdate_title_itemtotal_df(df_return_complete_removed)
    df_duplicate = find_duplicate(df_date_title_itmeorder_subset)
    render_df_as_duplicatehtml(df_duplicate)
    
    
    #create dafaframe for top 10 by year
    
    df_date_title_itemorder_year = create_year_column(df_date_title_itmeorder_subset)
    df_sorted_by_year_itemtotal = sort_by_year_itemtotal(df_date_title_itemorder_year)
    df_top10 = get_top10_eachyear(df_sorted_by_year_itemtotal)
    render_df_as_top10html(df_top10)
    
    #create the resul html
    create_html(output_filename)
    open_localfile(output_filename)
    
        
main()
    







