import psycopg2
from dbconnection_Scenerio import main
import datetime
# Get the current date in the desired format
current_date = datetime.datetime.now().strftime('%Y-%m-%d')  
# List of queries to execute 

def run_queries(use_case,user_id):
    queries = [
    # "-- insert colne inca p data into fact",
    f"""INSERT INTO inca_p_output_dsd_user_scenerio(
            date_, discharge, volume, velocity, water_depth, stream_power, shear_velocity, max_ent_grain_size, moveable_bed_mass, entrainment_rate, deposition_rate, bed_sediment, suspended_sediment, diffuse_sediment, water_column_tdp, water_column_pp, wc_sorption_release, stream_bed_tdp, stream_bed_pp, bed_sorption_release, macrophyte_mass, epiphyte_mass, water_column_tp, water_column_srp, water_temperature, tdp_input, pp_input, water_column_epc0, stream_bed_epc0, suspended_sediment_mass, mprop, settling_velocity, r, rmax, live_phytoplankton, dissolved_oxygen, bod, _saturation, reach, c_id, use_case, user_id) SELECT date_, discharge, volume, velocity, water_depth, stream_power, shear_velocity, max_ent_grain_size, moveable_bed_mass, entrainment_rate, deposition_rate, bed_sediment, suspended_sediment, diffuse_sediment, water_column_tdp, water_column_pp, wc_sorption_release, stream_bed_tdp, stream_bed_pp, bed_sorption_release, macrophyte_mass, epiphyte_mass, water_column_tp, water_column_srp, water_temperature, tdp_input, pp_input, water_column_epc0, stream_bed_epc0, suspended_sediment_mass, mprop, settling_velocity, r, rmax, live_phytoplankton, dissolved_oxygen, bod, _saturation, reach, 2,  '{use_case}', '{user_id}' FROM aquascope_mvp_bkp.colne_inca_p_scenerio""", 
    """ALTER TABLE inca_p_output_dsd_user_scenerio Drop COLUMN id""",
    """ALTER TABLE inca_p_output_dsd_user_scenerio ADD COLUMN id SERIAL PRIMARY KEY""",
    # "-- insert colne data into table",
    f"""INSERT INTO inca_n_output_dsd_user_scenerio(
            flow, nitrate, ammonium, volume, reach, date, c_id, use_case, user_id) SELECT flow, nitrate, ammonium, volume, reach, date, 2, '{use_case}', '{user_id}' FROM aquascope_mvp_bkp.colne_inca_n_scenerio""",
    """ALTER TABLE Inca_n_output_dsd_user_scenerio Drop COLUMN id""",
    """ALTER TABLEinca_n_output_dsd_user_scenerio ADD COLUMN id SERIAL PRIMARY KEY"""]


    for query in queries:
            try: 
                connection = main()
                cursor = connection.cursor()
                cursor.execute(query)
                print("Query executed successfully.")
                connection.commit()  
            except (Exception, psycopg2.Error) as error:
                print("Error executing queries:", error)
            finally:
                if connection:
                    cursor.close()
                    connection.close()
                    print("Connection closed.") 

         

        

