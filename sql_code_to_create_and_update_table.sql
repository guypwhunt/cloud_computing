/* Command to create the SQL table */ 
CREATE TABLE stock_data (
    pk_stock_id int,
    stock_name nvarchar(MAX),
    stock_symbol nvarchar(MAX))
	
/* Command to insert records into the SQL table */ 
INSERT INTO [dbo].[stock_data] ([pk_stock_id], [stock_name], [stock_symbol]) VALUES (1, 'IBM', 'IBM')