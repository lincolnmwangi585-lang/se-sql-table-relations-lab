# STEP 0

# SQL Library and Pandas Library
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('data.sqlite')

pd.read_sql("""SELECT * FROM sqlite_master""", conn)

# STEP 1
# who works in the boston office?
df_boston = pd.read_sql("""
    SELECT firstName, lastName
    FROM employees
    JOIN offices USING(officeCode)
    WHERE city = 'Boston';
""", conn)

# STEP 2
# any offices with no one in them?
df_zero_emp = pd.read_sql("""
    SELECT offices.officeCode, offices.city, COUNT(employeeNumber) AS n_employees
    FROM offices
    LEFT JOIN employees USING(officeCode)
    GROUP BY offices.officeCode
    HAVING n_employees = 0;
""", conn)

# STEP 3
# every employee + their office (left join so we don't drop anyone)
df_employee = pd.read_sql("""
    SELECT firstName, lastName, city, state
    FROM employees
    LEFT JOIN offices USING(officeCode)
    ORDER BY firstName, lastName;
""", conn)

# STEP 4
# customers who never ordered anything
df_contacts = pd.read_sql("""
    SELECT contactFirstName, contactLastName, phone, salesRepEmployeeNumber
    FROM customers
    LEFT JOIN orders USING(customerNumber)
    WHERE orderNumber IS NULL
    ORDER BY contactLastName;
""", conn)

# STEP 5
# payments high to low - amount is text so cast it first
df_payment = pd.read_sql("""
    SELECT contactFirstName, contactLastName, amount, paymentDate
    FROM customers
    JOIN payments USING(customerNumber)
    ORDER BY CAST(amount AS REAL) DESC;
""", conn)

# STEP 6
# reps whose customers avg over 90k credit
df_credit = pd.read_sql("""
    SELECT employeeNumber, firstName, lastName, COUNT(customerNumber) AS n_customers
    FROM employees
    JOIN customers ON employees.employeeNumber = customers.salesRepEmployeeNumber
    GROUP BY employeeNumber
    HAVING AVG(creditLimit) > 90000
    ORDER BY n_customers DESC;
""", conn)

# STEP 7
# best sellers by total units
df_product_sold = pd.read_sql("""
    SELECT productName,
           COUNT(orderNumber) AS numorders,
           SUM(quantityOrdered) AS totalunits
    FROM products
    JOIN orderdetails USING(productCode)
    GROUP BY productCode
    ORDER BY totalunits DESC;
""", conn)

# STEP 8
# how many different customers bought each product
df_total_customers = pd.read_sql("""
    SELECT productName,
           products.productCode,
           COUNT(DISTINCT customerNumber) AS numpurchasers
    FROM products
    JOIN orderdetails USING(productCode)
    JOIN orders USING(orderNumber)
    GROUP BY products.productCode
    ORDER BY numpurchasers DESC;
""", conn)

# STEP 9
# customers per office
df_customers = pd.read_sql("""
    SELECT COUNT(customerNumber) AS n_customers,
           offices.officeCode,
           offices.city
    FROM offices
    JOIN employees USING(officeCode)
    JOIN customers ON employees.employeeNumber = customers.salesRepEmployeeNumber
    GROUP BY offices.officeCode;
""", conn)

# STEP 10
# find the products barely anyone orders (< 20 customers), then who sold them
df_under_20 = pd.read_sql("""
    SELECT DISTINCT employeeNumber, firstName, lastName, offices.city, offices.officeCode
    FROM employees
    JOIN offices USING(officeCode)
    JOIN customers ON employees.employeeNumber = customers.salesRepEmployeeNumber
    JOIN orders USING(customerNumber)
    JOIN orderdetails USING(orderNumber)
    WHERE productCode IN (
        SELECT productCode
        FROM orderdetails
        JOIN orders USING(orderNumber)
        GROUP BY productCode
        HAVING COUNT(DISTINCT customerNumber) < 20
    )
    ORDER BY lastName;
""", conn)

conn.close()
