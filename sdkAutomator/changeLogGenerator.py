import os
import sys, re, logging

class changeLogGenerator():
    """
    To generate code in CHANGELOG file


    :param resources_list:
    :return:
    """
    def __init__(self, resources_dict, api_version):
        self.resources_dict = resources_dict
        self.api_version = api_version
        self.file_name = 'CHANGELOG.md'
        os.chdir('/home/venkatesh/Documents/oneview-python')
        self.list_of_linenos = self.search_for_string_starts_with_v()
        if self.list_of_linenos is not None and len(self.list_of_linenos) is not None:
            self.backup_lines,self.backup_mid,self.backup_end = self.backup_existing_content(self.file_name,self.list_of_linenos)
            self.added_integer = float(self.first_line[2:5])
        else:
            self.added_integer = "{:.1f}".format(float(self.first_line[2:5])+ float('0.1'))
        self.final_version = str(self.added_integer) + '.0'

    def delete_multiple_lines(self, linenos):
        """
        This deletes list of line numbers that got
        returned from search_for_string_starts_with_v.

        """
        start = int(linenos[0])
        end = int(linenos[1])
        with open(self.file_name, 'r+') as fp:
            lines = fp.readlines()
            fp.seek(0)
            fp.truncate()

            for number, line in enumerate(lines):
                if number not in range(start-1, end):
                    fp.write(line)

    def backup_existing_content(self, filename, linenos):
        """
        This deletes list of line numbers that got
        returned from search_for_string_starts_with_v.

        """
        start = 0
        mid = -1
        end = int(linenos[0])
        lines = []
        s = "Features supported with the current release"
        with open(filename, encoding='utf-8') as f:
            for position, line in enumerate(f,1):
                if ((position in range(start, end+1)) and (line.count(s)>0)):
                    mid = position+1

        if mid != -1:
            with open(filename, encoding='utf-8') as f:
                for position_new, line_new in enumerate(f, 1):
                    if position_new in range(mid,end+1):
                        lines.append(line_new)
        else:
            mid = None

        return lines,mid,end

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
                        if count == 1:
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

    def mergeContents(self, backup_lines, backup_mid, backup_end):
        """
        This merges content that got generated for new release with
        existing content in CHANGELOG
        """
        dummy_lines = []
        new_modules = []
        original_lines = []
        end = 0
        s = "Features supported with the current release"
        with open('dummy_CHANGELOG.md', encoding='utf-8') as f:
            for position, line in enumerate(f):
                end = end + 1
                if (line.count(s)>0):
                    mid = position
        with open('dummy_CHANGELOG.md', encoding='utf-8') as f:
            for position_new, line_new in enumerate(f):
                if position_new in range(mid+1, end):
                    dummy_lines.append(line_new)
                if position_new in range(0, mid-1):
                    original_lines.append(line_new)
        new_modules = dummy_lines + backup_lines
        new_modules_updated = []
        for module in new_modules:
            new_modules_updated.append(module.replace('\n','').replace('- ','').rstrip())
        new_modules = sorted(list(set(new_modules_updated)))
        self.delete_multiple_lines([backup_mid, backup_end])
        with open("test1.txt", "w") as test1:
            for ele in new_modules:
                test1.write("- {0} \n".format(str(ele)))
            test1.write("\n")
        with open("CHANGELOG.md", "r+") as f2:
            for x in range(backup_mid-1):
                f2.readline()   # skip past early lines
            pos = f2.tell() # remember insertion position
            f2_remainder = f2.read()    # cache the rest of f2
            f2.seek(pos)
            with open("test1.txt", "r") as f1:
                f2.write(f1.read())
                f2.write(f2_remainder)

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
            for ele in self.resources_dict.keys():
                modules.append(ele)
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

            if self.list_of_linenos and self.backup_mid is not None:
                self.mergeContents(self.backup_lines, self.backup_mid, self.backup_end)
            else:
                dummy_data += original_data
                with open("CHANGELOG.md", "w") as final:
                    final.write(dummy_data)

            print("--------Completed writing to CHANGELOG---------------")
        except Exception as e:
            print("Exception occurred while writing to CHANGELOG {0}".format(str(e)))
        finally:
            os.remove("dummy_CHANGELOG.md")
            os.remove("test1.txt")
                              