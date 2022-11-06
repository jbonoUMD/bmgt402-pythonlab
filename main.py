from flask import Flask, render_template, request
import datetime as dt
import db_connector as db
import data_format as df

app = Flask(__name__)


@app.context_processor
def inject_now():
    return {'now': dt.datetime.utcnow()}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        sql_table_name = request.form['frm_tableName']
        sql_column_name = request.form['frm_colName']
        sql_operator = request.form['frm_operator']
        sql_column_value = request.form['frm_colVal']

        cursor = db.get_connection()
        metadata = db.get_metadata(cursor, sql_table_name)
        results = db.execute_query(cursor, f"SELECT * FROM {sql_table_name} \
                                             WHERE {sql_column_name} {sql_operator} ?", sql_column_value)

        return render_template('search.html', params=request.form, metadata=metadata, results=results)

    else:
        return render_template('search.html', params=request.form)


@app.route('/insert_one_table')
def insert_one_table():
    return render_template('insert_one_table.html')


@app.route('/insert_one_table_process', methods=['POST'])
def insert_one_table_process():
    sql_table_name = request.form['frm_tableName']

    cursor = db.get_connection()
    results = db.fetch_all(cursor, sql_table_name)

    metadata = db.get_metadata(cursor, sql_table_name)

    return render_template('insert_one_table_process.html', params=request.form, metadata=metadata, results=results)


@app.route('/insert_one_table_add_record', methods=['POST'])
def insert_one_table_add_record():
    sql_table_name = request.form['frm_tableName']

    insert_fields = df.format_db_fields(request.form)

    columns = str(list(insert_fields.keys())).replace("'", "")[1:-1]
    values = str(list(insert_fields.values()))[1:-1]

    cursor = db.get_connection()

    sql = f"INSERT INTO {sql_table_name} ({columns}) VALUES ({values})"
    success = db.update_query(cursor, sql)
    insert_query = sql.replace('VALUES', '<br />VALUES')

    results = db.fetch_all(cursor, sql_table_name)
    metadata = db.get_metadata(cursor, sql_table_name)

    return render_template('insert_one_table_process.html', params=request.form, metadata=metadata,
                           results=results, success=success, query=insert_query)


@app.route('/insert_relationship')
def insert_relation():
    return render_template('insert_relationship.html')


@app.route('/insert_relationship_process', methods=['POST'])
def insert_relationship_process():
    sql_parent_table = request.form['frm_parentTable']
    sql_child_table = request.form['frm_childTable']
    sql_parent_primary_key = request.form['frm_parentPrimaryKey']
    sql_parent_primary_key_value = request.form['frm_parentPrimaryKeyValue']
    sql_child_foreign_key = request.form['frm_childForeignKey']

    cursor = db.get_connection()
    parent_metadata = db.get_metadata(cursor, sql_parent_table)
    child_metadata = db.get_metadata(cursor, sql_child_table)

    parent_results = db.execute_query(cursor, f"SELECT * FROM {sql_parent_table} \
                                               WHERE {sql_parent_primary_key} = {sql_parent_primary_key_value}")

    child_results = db.execute_query(cursor, f"SELECT * FROM {sql_child_table} \
                                               WHERE {sql_child_foreign_key} = {sql_parent_primary_key_value}")

    return render_template('insert_relationship_process.html', params=request.form, parent_metadata=parent_metadata,
                           child_metadata=child_metadata, parent_results=parent_results, child_results=child_results)


@app.route('/insert_relationship_add_record', methods=['POST'])
def insert_relationship_add_record():
    sql_parent_table = request.form['frm_parentTable']
    sql_child_table = request.form['frm_childTable']
    sql_parent_primary_key = request.form['frm_parentPrimaryKey']
    sql_parent_primary_key_value = request.form['frm_parentPrimaryKeyValue']
    sql_child_foreign_key = request.form['frm_childForeignKey']

    insert_fields = df.format_db_fields(request.form)

    columns = str(list(insert_fields.keys())).replace("'", "")[1:-1]
    values = str(list(insert_fields.values()))[1:-1]

    cursor = db.get_connection()

    sql = f"INSERT INTO {sql_child_table} ({columns}) VALUES ({values})"
    success = db.update_query(cursor, sql)
    insert_query = sql.replace('VALUES', '<br />VALUES')

    parent_metadata = db.get_metadata(cursor, sql_parent_table)
    child_metadata = db.get_metadata(cursor, sql_child_table)
    parent_results = db.execute_query(cursor, f"SELECT * FROM {sql_parent_table} \
                                               WHERE {sql_parent_primary_key} = {sql_parent_primary_key_value}")
    child_results = db.execute_query(cursor, f"SELECT * FROM {sql_child_table} \
                                               WHERE {sql_child_foreign_key} = {sql_parent_primary_key_value}")

    return render_template('insert_relationship_process.html',  params=request.form,
                           parent_metadata=parent_metadata, child_metadata=child_metadata,
                           parent_results=parent_results, child_results=child_results, success=success,
                           query=insert_query)


@app.route('/delete_one_table')
def delete_one_table():
    return render_template('delete_one_table.html')


@app.route('/delete_one_table_process', methods=['POST'])
def delete_one_table_process():
    sql_table_name = request.form['frm_tableName']

    cursor = db.get_connection()
    results = db.fetch_all(cursor, sql_table_name)

    metadata = db.get_metadata(cursor, sql_table_name)

    return render_template('delete_one_table_process.html', params=request.form, metadata=metadata, results=results)


@app.route('/delete_one_table_remove_record', methods=['POST'])
def delete_one_table_remove_record():
    sql_table_name = request.form['frm_tableName']
    sql_primary_key = request.form['frm_primaryKeyName']
    sql_primary_key_value = request.form['frm_deletePrimaryKeyValue']

    cursor = db.get_connection()

    sql = f"DELETE FROM {sql_table_name} \
            WHERE {sql_primary_key} = {sql_primary_key_value}"

    success = db.update_query(cursor, sql)
    delete_query = sql.replace('WHERE', '<br />WHERE')

    results = db.fetch_all(cursor, sql_table_name)
    metadata = db.get_metadata(cursor, sql_table_name)

    return render_template('delete_one_table_process.html', params=request.form, metadata=metadata,
                           results=results, success=success, query=delete_query)


if __name__ == "__main__":
    # Quick test configuration. Please use proper Flask configuration options
    # in production settings, and use a separate file or environment variables
    # to manage the secret key!
    app.debug = True
    app.run(host='localhost', port=9000)
