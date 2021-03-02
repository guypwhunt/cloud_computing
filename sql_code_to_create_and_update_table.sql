/* Command to create the SQL table */ 
CREATE TABLE index_data (
    pk_index_id int,
    index_name nvarchar(MAX),
    index_symbol nvarchar(MAX))
	
/* Command to insert records into the SQL table */ 
INSERT INTO [dbo].[index_data] ([pk_index_id], [index_name], [index_symbol]) VALUES (1, 'FTSE 100', 'UKX')
INSERT INTO [dbo].[index_data] ([pk_index_id], [index_name], [index_symbol]) VALUES (2, 'FTSE 250', 'MCX')
INSERT INTO [dbo].[index_data] ([pk_index_id], [index_name], [index_symbol]) VALUES (3, 'FTSE 350', 'NMX ')
