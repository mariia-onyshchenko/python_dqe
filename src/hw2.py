import random
import string

class task_2():
    def create_dicts():
        num_dicts = random.randint(2, 10)  
        def gen_dicts(num_dicts):
            dicts = []
            for i in range(num_dicts):
                amount_keys = random.randint(1, 5) 
                keys = random.sample(string.ascii_letters, amount_keys)  
                single_dict = {key: random.randint(0, 100) for key in keys}  #randint includes both upper and lower boundaries
                dicts.append(single_dict)
            return dicts

        def add_dicts(dicts):
            super_dict = {}
            key_duplicates = {}

            for indx, single_dict in enumerate(dicts):
                for key, value in single_dict.items():
                    if key in super_dict:
                        if value > super_dict[key][0]:
                            super_dict[key] = (value, indx + 1)  
                        key_duplicates[key].add(indx + 1)  
                    else:
                        super_dict[key] = (value, indx + 1)  
                        key_duplicates[key] = {indx + 1}  

            final_dict = {}
            for key, (value, dict_num) in super_dict.items():
                if len(key_duplicates[key]) > 1:  
                    final_key = f"{key}_{dict_num}"
                else:  
                    final_key = key
                final_dict[final_key] = value
            return final_dict
        random_dicts = gen_dicts(num_dicts)
        final_dict = add_dicts(random_dicts)
        return final_dict

task_2.create_dicts()