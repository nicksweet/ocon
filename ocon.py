import json
import sys
import os
import shutil
from os.path import abspath, dirname, isdir


class ClassGenerator():
    def __init__(self, class_name, class_dir, class_properties, enumerations, property_values,
                super_class_name, super_class_properties, imports, delegates):
        self.class_name = class_name
        self.upper_class_name = ''
        self.class_dir = class_dir
        self.class_properties = class_properties
        self.enumerations = enumerations
        self.property_values = property_values
        self.super_class_name = super_class_name
        self.super_class_properties = super_class_properties
        self.imports = imports
        self.delegates = delegates

    def make_header_and_imp_files(self):
        class_name = str(self.class_name)
        first_letter = class_name[:1].upper()
        self.upper_class_name = first_letter + class_name[1:]
        self.class_dir = self.class_dir + self.upper_class_name + '/'
        if isdir(self.class_dir):
            user_input = raw_input("\n\Directory %s already exists. Would you like to remove it?.\n\n'yes' or 'no'\n\n" % self.class_dir)
            if user_input == "yes":
                shutil.rmtree(self.class_dir)
                print "The directory %s has been removed\n\n" % self.class_dir
            elif user_input == "no":
                'program exiting now...'
                sys.exit()
            else:
                print "Input not 'yes' or 'no' program will exit now..."
                sys.exit()

        os.mkdir(self.class_dir)
        header_file_path = self.class_dir + self.upper_class_name + '.h'
        imp_file_path = self.class_dir + self.upper_class_name + '.m'
        header_file = open(header_file_path, 'w')
        imp_file = open(imp_file_path, 'w')
        return header_file, imp_file

    def write_header_file(self, header_file):
        header_file_imports_and_delegates = ''
        if self.super_class_name:
            header_file_imports_and_delegates = '#import "' + self.super_class_name + '.h"\n'
        if self.imports:
            for import_name in self.imports:
                header_file_imports_and_delegates += '#import "' + import_name + '.h"\n'

        header_file_imports_and_delegates += '\n@interface ' + self.upper_class_name + ' : ' + self.super_class_name


        #write delegates
        if self.delegates:
            header_file_imports_and_delegates += ' <'
            for i, delegate_name in enumerate(self.delegates):
                if i != 0 and i < len(self.delegates):
                    header_file_imports_and_delegates += ', '
                header_file_imports_and_delegates += delegate_name
            header_file_imports_and_delegates += '>\n\n'

        header_file.write(header_file_imports_and_delegates)

        if self.class_properties:
            self.class_properties = [prop for prop in self.class_properties if prop not in self.super_class_properties]
            #super_property_list = [prop for prop in self.super_class_properties if prop not in self.class_properties]
            for prop in self.class_properties:
                if prop[0][len(prop[0])-1] == '*':
                    property_attrs_h = '(nonatomic, readonly, strong) '
                else:
                    property_attrs_h = '(readonly) '
                prop_str_h = '@property ' + property_attrs_h + prop[0] + ' ' + prop[1] + ';\n'
                header_file.write(prop_str_h)

        if self.enumerations:
            for enumeration in self.enumerations:
                enumerations_str = '\n\ntypedef enum \n{'

                for i, enum in enumerate(enumeration['enumerationValues']):
                    if i != 0:
                        enumerations_str += ",\n\t%s" % enum
                    else:
                        enumerations_str += "\n\t%s" % enum
                enumerations_str += "\n}%s;" % enumeration['enumerationName']
                header_file.write(enumerations_str)

    def write_imp_file(self, imp_file):
        imp_file_contents = ''

        if self.imports:
            for import_name in self.imports:
                imp_file_contents += '#import "' + import_name + '.h"\n'
        #redec props and interface
        if self.class_properties:
            imp_file_contents += '\n@interface ' + self.upper_class_name + '()\n\n'
            for prop in self.class_properties:

                if prop[0][len(prop[0])-1] == '*':
                    property_attrs_m = '(nonatomic, readwrite, strong) '
                else:
                    property_attrs_m = '(readwrite) '

                imp_file_contents += '\t@property ' + property_attrs_m + prop[0] + ' ' + prop[1] + ';\n'
            imp_file_contents += '\n@end\n'

        imp_file_contents += '\n@implementation ' + self.upper_class_name + '\n\n'

        imp_file.write(imp_file_contents)

        if self.class_properties:
            self.class_properties = [prop for prop in self.class_properties if prop not in self.super_class_properties]
            #super_property_list = [prop for prop in self.super_class_properties if prop not in self.class_properties]
            for prop in self.class_properties:
                prop_str_m = '@synthesize ' + prop[1] + ' = _' + prop[1] + ';\n'
                imp_file.write(prop_str_m)

    def write_init_function(self, header_file, imp_file):
        if self.class_properties or self.super_class_properties:
            #remove properties that have all ready been assigned in parent classes from properties list
            if self.class_properties and self.property_values:
                unassigned_class_props = [prop for prop in self.class_properties if prop[1] not in self.property_values.keys()]
            else:
                unassigned_class_props = self.class_properties

            if self.super_class_properties and self.property_values:
                unassigned_super_class_props = [prop for prop in self.super_class_properties if prop[1] not in self.property_values.keys()]
            else:
                unassigned_super_class_props = self.super_class_properties

            init_func_h = init_func_m = '\n\n- (id)init'

            #CREATE INITMETHOD NAME BY FIRST WRITING ANY SUPER CLASS PROPS THAT HAVE NOT YET BEEN ASSIGNED, THEN BY WRITING
            #ANY CLASS PROPS THAT DO NOT HAVE PREDETERMANED VALUES.
            if unassigned_super_class_props:
                for i, prop in enumerate(unassigned_super_class_props):
                    if i == 0:
                        cap_prop = prop[1][0].upper() + prop[1][1:]
                        init_func_h = init_func_m = init_func_h + 'With' + cap_prop + ': (' + prop[0] + ')' + prop[1]
                    else:
                        init_func_h = init_func_m = init_func_h + ' ' + prop[1] + ':(' + prop[0] + ')' + prop[1]

                if unassigned_class_props:
                    for type, name in unassigned_class_props:
                        init_func_h = init_func_m = init_func_h + ' ' + name + ':(' + type + ')' + name

            elif unassigned_class_props:
                for i, prop in enumerate(unassigned_class_props):
                    if i == 0:
                        cap_prop = prop[1][0].upper() + prop[1][1:]
                        init_func_h = init_func_m = init_func_h + 'With' + cap_prop + ': (' + prop[0] + ')' + prop[1]
                    else:
                        init_func_h = init_func_m = init_func_h + ' ' + prop[1] + ':(' + prop[0] + ')' + prop[1]

            #CREATE CALL TO SUPER CLASS CONSTRUCTOR BY WRITING ANY SUPER CLASS PROPERTIES THAT HAVE NOT YET
            #BEEN ASSIGNED. IF ONE OF THERE VALUES WAS GIVEN IN THIS IN THIS CLASS, ASSIGN THAT VALUE, OTHERWISE
            #ASSIGN IT TO THAT ARG SENT IN THIS CLASSES INIT METHOD.
            init_func_m += '\n{\n\tif (self = [super init'
            if unassigned_super_class_props:
                for i, prop in enumerate(unassigned_super_class_props):
                    if i == 0:
                        cap_prop = prop[1][0].upper() + prop[1][1:]
                        init_func_m += "With" + cap_prop + ':' + prop[1]
                    else:
                        init_func_m += ' ' + prop[1] + ':' + prop[1]

                for prop_type, prop_name in self.super_class_properties:
                    #check if this property has been assigned in class_properties
                        #get prop val
                    if self.property_values.get(prop_name):
                        val_for_prop = self.property_values[prop_name]
                        #self.property_values.pop(prop_name)

                        init_func_m += ' ' + prop_name + ':' + str(val_for_prop)

            else:
                for i, prop in enumerate(self.super_class_properties):
                    if i == 0:
                        cap_prop = prop[1][0].upper() + prop[1][1:]
                        init_func_m += "With" + cap_prop + ':'
                    else:
                        init_func_m += ' ' + prop[1] + ':'

            init_func_m += '])\n\t{'

            #IF PROPERTIES FOR THIS CLASS HAVE VALUES ASSIGNED SET THEM TO THAT VALUE, OTHERWISE SET THEM
            #TO THE ARGUEMENT PASSED IN OF THE SAME NAME.
            for prop_type, prop_name in self.class_properties:
                if prop_name in  self.property_values:
                    print "gogo ", prop_name
                    prop_val = self.property_values[prop_name]
                    init_func_m += '\n\t\tself.' + prop_name + ' = ' + prop_val + ';'
                else:
                    init_func_m += '\n\t\tself.' + prop_name + ' = ' + prop_name + ';'

            init_func_m += '\n\t}'
            init_func_m += '\n\treturn self;'
            init_func_m += '\n}\n\n@end'
            init_func_h += ';\n\n@end'

            header_file.write(init_func_h)
            imp_file.write(init_func_m)


if __name__ == '__main__':
    this_dir = dirname(abspath(__file__)) + '/'
    json_path = sys.argv[1]
    json_file = open(json_path)
    json_dict = json.loads(json_file.read())
    json_file.close()
    processed_classes = {}

    def get_inherited_props_and_values(super_class_name):
        inherited_props = []
        all_assigned_propertie_values = {}
        super_class_name2 = super_class_name

        while True:
            if processed_classes.get(super_class_name2, False):
                assigned_values = processed_classes[super_class_name2].get('assigned_values', {})

                if assigned_values:
                    for prop in assigned_values:
                        all_assigned_propertie_values[prop] = assigned_values[prop]

                super_class_name2 = processed_classes[super_class_name2].get('super_class_name')
            else:
                break

        while True:
            if processed_classes.get(super_class_name, False):
                super_class_props = processed_classes[super_class_name].get('properties', [])

                if super_class_props:
                    super_class_props.reverse()
                    [inherited_props.insert(0, prop) for prop in super_class_props]

                [inherited_props.remove(prop) for prop in inherited_props if prop[1] in all_assigned_propertie_values]
                super_class_name = processed_classes[super_class_name].get('super_class_name')
            else:
                break
        return all_assigned_propertie_values, inherited_props

    #super_property_list is a list of pairs of property types and property names
    def make_classes(json_dict, accum_path, super_class_name):
        class_names = json_dict.keys()
        for class_name in class_names:
            class_properties = json_dict[class_name].get('pairsOfPropertyTypesAndPropertyNames', [])
            enumerations = json_dict[class_name].get('enumerations', [])
            property_values = json_dict[class_name].get('values', {})
            imports = json_dict[class_name].get('imports', [])
            delegates = json_dict[class_name].get('delegates', [])
            class_properties_copy = class_properties[:]

            all_assigned_properties_values, super_class_properties = get_inherited_props_and_values(super_class_name.lower())

            for prop in property_values:
                all_assigned_properties_values[prop] = property_values[prop]

            class_generator = ClassGenerator(class_name=class_name,
                                            class_dir=accum_path,
                                            class_properties=class_properties,
                                            property_values=all_assigned_properties_values,
                                            enumerations=enumerations,
                                            super_class_name=super_class_name,
                                            super_class_properties=super_class_properties,
                                            imports=imports,
                                            delegates=delegates)

            header_file, imp_file = class_generator.make_header_and_imp_files()
            class_generator.write_imp_file(imp_file)
            class_generator.write_header_file(header_file)
            class_generator.write_init_function(header_file, imp_file)

            header_file.close()
            imp_file.close()

            processed_classes[class_name.lower()] = {'properties': class_properties_copy,
                                                    'assigned_values': property_values,
                                                    'super_class_name': super_class_name.lower()}
            the_class = json_dict[class_name]
            if the_class.get('subclasses', False):
                subclasses = the_class["subclasses"]
                make_classes(json_dict=subclasses,
                            accum_path=class_generator.class_dir,
                            super_class_name=class_generator.upper_class_name)

    make_classes(json_dict=json_dict,
                accum_path=this_dir,
                super_class_name='')
