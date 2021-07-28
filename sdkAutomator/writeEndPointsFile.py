import sys
import dataScraping

class writeEndpointsFile(object):
    resource_names = []
    def __init__(self, product_table_name, executed_files, is_ansible):
        self.line_nos = {}
        self.res_lines = {}
        self.product_table_name = product_table_name
        self.all_lines = None
        self.executed_files = executed_files
        self.is_ansible = is_ansible
        self.current_version = None

    def write_md(self):
        """
        To generate code in endpoints-support.md file
        """        
        try:
            with open('endpoints-support.md', 'w') as file:
                file.writelines(self.all_lines)
        except IOError as e:
            print ("I/O error({0}): {1}".format(e.errno, e.strerror))
        except:
            print("Unexpected error while writing in endpoints file file: {}", sys.exc_info()[0])


    def load_md(self):
        """
        To read data from endpoints-support.md file
        """
        try:
            with open('endpoints-support.md') as file:
                self.all_lines = file.readlines()
        except IOError as e:
            print ("I/O error({0}): {1}".format(e.errno, e.strerror))
        except:
            print("Unexpected error while reading from endpoints file file: {}", sys.exc_info()[0])       

    def add_column(self, product_table_name):
        """
        To add a empty column in endpoints-support.md file 
        till end of file with new API version in header 
        only once
        """
        count = 0
        self.load_md()
        for line in self.all_lines:
            count += 1
            if product_table_name in line:
                break

        head_line = self.all_lines[count + 1].split()
        self.current_version = int(head_line[-2].split('V')[-1])
        new_version = 'V' + str(self.current_version + 200)
        if int(self.self.api_version) == self.current_version:
            return

        column_added = False
        while count < len(self.all_lines):
            add_col = None
            line = self.all_lines[count].rstrip('\n')

            if "Endpoints" in self.all_lines[count]:
                add_col = line + " " + new_version + '               |\n'

            elif "---------" in self.all_lines[count]:
                add_col = line + ' :-----------------: |\n'
                column_added = True

            if add_col:
                self.all_lines[count] = add_col
                self.write_md()

            if column_added:
                break

            count += 1

    def get_rows(self, resource_name):
        """
        To get row numbers according to a resource 
        to mark with required marks.
        """
        count = 0
        resource_name_row_start = 0
        resource_name_row_end = 0
        self.load_md()
        for line in self.all_lines:
            count += 1
            if line.startswith('|     '+resource_name):
                resource_name_row_start = count

                for no in range(count, len(self.all_lines)):
                    if self.all_lines[no].startswith('|     **'):
                        resource_name_row_end = no
                        break

                return resource_name_row_start, resource_name_row_end

    def get_lines(self, st_no, end_no):
        """
        To get list of lines from starting
        line number to ending line number.
        """
        lines = list()
        self.load_md()
        for no in range(st_no, end_no):
            lines.append(dict({'line_no': no, 'line': self.all_lines[no]}))
        return lines

    def get_old_end_points(self, st_no, end_no, webscraping_data):
        lines = self.get_lines(st_no, end_no)

        end_points_list = []
        old_end_points = []
        for ele in lines:
            line = ele.get('line')
            if line.startswith('|<sub>'):
                ln = line.split('|')
                split_module = ln[1].strip().split('<sub>')
                module = split_module[-1].split('</sub>')[0]
                end_points_list.append({module, ''.join((ln[2].split()))})

        for end_point in end_points_list:
            data_found = False
            for data in webscraping_data:
                if data == end_point:
                    data_found = True
                    break
            if not data_found:
                old_end_points.append(end_point)
        return old_end_points

    def validate_webscrapping_data(self, lines, end_point, str):
        self.current_version = int(self.api_version) - 200
        end_point_found = False
        for ele in lines:
            line_no = ele.get('line_no')
            line = ele.get('line')
            if line.startswith('|<sub>'):
                ln = line.split('|')
                ln_length = len(ln)
                desired_length = int(((((self.current_version+200)-800)/200)+3))
                split_module = ln[1].strip().split('<sub>')
                module = split_module[-1].split('</sub>')[0]
                if end_point == {module, ln[2].strip()}:
                    ln = line.rstrip('\n')
                    if (ln_length == desired_length):
                        add_col = ln + str
                        self.all_lines[line_no] = add_col
                    else:
                        pass
                    end_point_found = True
                    break
        if not end_point_found:
            return end_point
        return

    def add_checks(self, st_no, end_no, webscraping_data):
        """
        To add marks in required places.
        """
        lines = self.get_lines(st_no, end_no)

        old_end_points = self.get_old_end_points(st_no, end_no, webscraping_data)
        for old_end_point in old_end_points:
            self.validate_webscrapping_data(lines, old_end_point, '  :heavy_minus_sign:   |\n')

        new_end_points = []
        for end_point in webscraping_data:
            new_end_point = self.validate_webscrapping_data(lines, end_point, '  :white_check_mark:   |\n')
            if new_end_point:
                new_end_points.append(new_end_point)
        # below code is to add new endpoints into endpoints-support.md file and its commented, parked aside 
        # for end_point in new_end_points:
        #     if (len(list(end_point)[1]) > 5):
        #         add_col = '|<sub>'+list(end_point)[1]+'</sub>                                                      |'+' '+list(end_point)[0]+'      '+ '|  :heavy_minus_sign:   '*int(((((self.current_version+200)-800)/200)-1))+'|  :white_check_mark:   |\n'
        #     else:
        #         add_col = '|<sub>'+list(end_point)[0]+'</sub>                                                      |'+' '+list(end_point)[1]+'      '+ '|  :heavy_minus_sign:   '*int(((((self.current_version+200)-800)/200)-1))+'|  :white_check_mark:   |\n'            
        #     line_no = lines[-1].get('line_no')
        #     self.all_lines[line_no] = self.all_lines[line_no]+add_col
        #     self.write_md()
        #     self.load_md()
        #     lines.append(dict({'line_no':line_no+1, 'line':self.all_lines[line_no+1]}))

    def main(self):

        i = 0
        if self.selected_sdk == 'ansible':
            exe = modifyExecutedFiles(self.executed_files)
            self.executed_files = exe
        else:
            pass
        print("------Initiating write to endpoints file--------")
        for ele in self.executed_files:
            resource = list(self.resource_dict.keys())[list(self.resource_dict.values()).index(ele)]
            formatted_resource_name = '**' + resource + '**'
            self.resource_names.append(formatted_resource_name)
        self.add_column(self.product_table_name)
        for resource_name in self.resource_names:
            webscraping_data = dataScraping(self.executed_files[i])
            data_returned_from_web_scraping = webscraping_data.data_scraped()
            st_no, end_no = self.get_rows(resource_name)
            self.add_checks(st_no, end_no, data_returned_from_web_scraping)
            i = i + 1
            self.write_md()
        print("-------Completed write to endpoints file--------")