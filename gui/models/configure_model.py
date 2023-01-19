import sqlite3

from tkinter import StringVar

TABLE_NAME = 'configure'

# Constants

class ConfigureModel:
    """ Model for the Configure Frame """
    def __init__(self, db_name, cursor, connection) -> None:
        # Setup the database connection
        self.db_name = db_name
        self.unit = db_name[-4]
        self.cursor = cursor
        self.connection = connection
        #try:
        #    self.drop_table()
        #except:
        #    pass
        self.create_table()
        # Add the initial default values if necessary
        try:
            self.insert(1, "Tip Box", '1000', '1000', '1000', '1000', '50', '50', '50', '50', '50', '50', '50', '50')
            self.insert(2, "TEC Address", 'A', '1')
            self.insert(3, "TEC Address", 'B', '2')
            self.insert(4, "TEC Address", 'C', '3')
            self.insert(5, "TEC Address", 'D', '4')
            self.insert(6, "TEC Address", "Aux Heater A", '5')
            self.insert(7, "TEC Address", "Aux Heater B", '6')
            self.insert(8, "TEC Address", "Aux Heater C", '7')
            self.insert(9, "TEC Address", "Aux Heater D", '8')
            self.insert(10, "TEC Address", "Pre-Amp Thermocycler", '9')
        except:
            pass

    def create_table(self) -> None:
        """ Query for creating the Configure table 
        This table allows up to 12 values, the point of 12 is because that is the most amount of data necessary for one particular thing on
        the configure tab (tip box configuration), this table allows for all configuration data to be stored in one table and 
        it can be looked up by the NAME.
        """
        query = f"""CREATE TABLE IF NOT EXISTS {TABLE_NAME}(
        ID INT NOT NULL,
        NAME TEXT NOT NULL,
        VAL1 TEXT,
        VAL2 TEXT,
        VAL3 TEXT,
        VAL4 TEXT,
        VAL5 TEXT,
        VAL6 TEXT,
        VAL7 TEXT,
        VAL8 TEXT,
        VAL9 TEXT,
        VAL10 TEXT,
        VAL11 TEXT,
        VAL12 TEXT
        );
        """

    def drop_table(self) -> None:
        """ Drops the table out of the database """
        query = f"DROP TABLE {TABLE_NAME}"
        self.cursor.execute(query)

    def select(self, ID: int = None, name: str = None, val1: str = None) -> list:
        """ Select query which should be used in 4 ways
            1. Look up by ID (select(ID))
            2. Look up by NAME and VAL1 (select(name, val1))
            3. Look up by NAME (select(name))
            4. Look up the entire table (select())
        """
        if ID == None and name == None and val1 == None:
            query = f"SELECT * FROM {TABLE_NAME}"
        elif ID != None and (name == None and val1 == None):
            query = f"""SELECT * FROM {TABLE_NAME}
            WHERE ID = {ID}
            """
        elif ID == None and (name != None and val1 != None):
            query = f"""SELECT * FROM {TABLE_NAME}
            WHERE NAME = '{name}' AND VAL1 = '{val1}'
            """
        elif (ID == None and val1 == None) and name != None:
            query = f"""SELECT * FROM {TABLE_NAME}
            WHERE NAME = '{name}'
            """
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return results

    def insert(self,
               ID: int,
               name: str,
               val1: str,
               val2: str,
               val3: str,
               val4: str,
               val5: str,
               val6: str,
               val7: str,
               val8: str,
               val9: str,
               val10: str,
               val11: str,
               val12: str
    ) -> None:
        """ Insert query for the Configure Table """
        query = f"""INSERT INTO {TABLE_NAME}
        (
        ID,
        NAME,
        VAL1,
        VAL2,
        VAL3,
        VAL4,
        VAL5,
        VAL6,
        VAL7,
        VAL8,
        VAL9,
        VAL10,
        VAL11,
        VAL12
        )
        VALUES (
        {ID},
        '{name}',
        '{val1}',
        '{val2}',
        '{val3}',
        '{val4}',
        '{val5}',
        '{val6}',
        '{val7}',
        '{val8}',
        '{val9}',
        '{val10}',
        '{val11}',
        '{val12}',
        );
        """
        self.cursor.execute(query)
        self.connection.commit()

    def delete(self, ID: int) -> None:
        """ Query for deleting an item from the Configure Table """
        query = f"""DELETE FROM {TABLE_NAME}
        WHERE ID = {ID}
        """
        self.cursor.execute(query)
        self.connection.commit()