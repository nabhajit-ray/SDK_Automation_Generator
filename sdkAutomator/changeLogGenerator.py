import os
import fileinput, sys, re, logging
from sdkAutomator.executeResources import executeResources

class ChangeLogGenerator(executeResources):
    """
    To generate code in CHANGELOG file


    :param resources_list:
    :return:
    """
    def __init__(self, resources_list):
        super(ChangeLogGenerator).__init__()
        self.resources_list = resources_list
        self.file_name = 'CHANGELOG.md'
        path_parent = os.path.dirname(os.getcwd())
        os.chdir(path_parent)
        list_of_linenos = self.search_for_string_starts_with_v(self)
        if list_of_linenos is not None and len(list_of_linenos) is not None:
            self.delete_multiple_lines(self, list_of_linenos)
            self.added_integer = float(self.first_line[2:5])
        else:
            self.added_integer = float(self.first_line[2:5]) + float('0.1')
        self.final_version = str(self.added_integer) + '.0'

    def delete_multiple_lines(self, linenos):
        """
        This deletes list of line numbers that got 
        returned from search_for_string_starts_with_v.

        """
        start = int(linenos[0])
        end = int(linenos[1])
        count = end - start
        for line in fileinput.input(self.file_name, inplace=1, backup='.orig'):
            if start <= fileinput.lineno() < start + count:
                pass
            else:
                print(line[:-1])
        fileinput.close()

    def search_for_string_starts_with_v(self):
        """
        This is required to maintain idompotency. In case if any 
        code is generated for failure run, it deletes the previously
        generated code and make sure that the content in CHANGELOG is 
        in consistent state.
        This returns list of line numbers to be deleted.

        """
        line_number = 0
        count = 0
        list_of_results = []
        try:
            with open(self.file_name, 'r') as changelog_file:
                self.first_line = changelog_file.readline()
                if(self.first_line[8:18] == 'unreleased' or self.first_line[8:18] == 'Unreleased'):
                    for line in changelog_file:
                        if count == 2:
                            break
                        else:
                            line_number += 1
                            if re.search("^#\s([0-9][.]*){2}", line):
                                list_of_results.append(line_number)
                                count += 1
                    return list_of_results
        except IOError as e:
            print ("I/O error({0}): {1}".format(e.errno, e.strerror))
        except:
            print("Unexpected error while reading Changelog file: {}", sys.exc_info()[0])


    def write_data(self):
        """
        In case if any of the value for the key is not present,
        then it raises an exception, but will continue further and
        can add existing modules other than the missing one.

        Output will look like:
        ##### Features supported with the current release(v5.0.0)
        - FC Network
        - FCOE-Network
        """
        modules = []
        oneview_api_version = 'OneView ' + 'v' + str(self.added_integer)
        try:
            for ele in self.resources_list:
                modules.append(list(self.resource_dict.keys())[list(self.resource_dict.values()).index(ele)])
        except Exception as e:
            logging.debug("Unable to find a module {0}".format(str(e)))

        print("--------Started writing to CHANGELOG---------------")
        try:
            with open("dummy_CHANGELOG.md", "w") as dummy_file:
                dummy_file.write("# {}(unreleased)".format(str(self.final_version)))
                dummy_file.write("\n#### Notes\n")
                dummy_file.write("Extends support of the SDK to OneView REST API version {} ({})".format(str(self.api_version),str(oneview_api_version)))
                dummy_file.write("\n\n##### Features supported with the current release\n")
                for ele in sorted(modules):
                    dummy_file.write("- {0} \n".format(str(ele)))
                dummy_file.write("\n")

            with open("CHANGELOG.md", "r") as original_file:
                original_data = original_file.read()

            with open("dummy_CHANGELOG.md", "r") as dummy_file:
                dummy_data = dummy_file.read()

            dummy_data += original_data
            with open("CHANGELOG.md", "w") as final:
                final.write(dummy_data)

            print("--------Completed writing to CHANGELOG---------------")
        except Exception as e:
            print("Exception occurred while writing to CHANGELOG {0}".format(str(e))) 
        finally:
            os.remove("dummy_CHANGELOG.md")
