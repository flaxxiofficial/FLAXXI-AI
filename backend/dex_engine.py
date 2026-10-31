from androguard.core.dex import DEX


def analyze_dex(data):

    dex = DEX(data)

    classes = []

    for cls in dex.get_classes():

        classes.append({

            "class_name":cls.get_name(),

            "methods":[
                method.get_name()
                for method in cls.get_methods()
            ]

        })

    return {
        "total_classes":len(classes),
        "classes":classes[:500]
    }
