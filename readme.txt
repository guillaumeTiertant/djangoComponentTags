Django tag component

Le but de ce projet est de créer composants HTML réutilisables dans un projet Django.
Ces composants devait permettre d'intégrer des éléments de templates mais aussi de restituer des dépendances css et javascript.

Ce projet est inspiré de 2 projets qui on été modifié par la suite:
    - https://github.com/divio/django-classy-tag
    - https://github.com/EmilStenstrom/django-components

J'ai décidé d'utiliser le projet de divio pour ces classes basé sur les template tags ainsi que son parsage de block.
Néanmoins le parsage des arguments était assez éloigné de ce que je souhaitais pour mon projet.
En effet le parsage des arguments devais permettre l'ecriture d'un tag à la manière des balises html.

J'ai décidé d'utiliser le projet d'EmilStenstrom pour son système d'integration des dépendances de composants.

1 - Exemple :

Depuis templatetags/example.py:
    from component_tags.arguments import Argument, Flag, KeywordArgument
    from component_tags.core import Options, Tag, registry
    from django import template

    register = template.Library()

    class TestTag(Tag):
        name = 'mytest'
        options = Options(
            Argument(name='myarg'),
            KeywordArgument(name='mykwarg'),
            Flag(name='myflag'),
            blocks = [('block_a', 'nodelist_a'), ('node_b', 'blocklist_b')]
        )

        class Media:
            template = "components/test.html"
            css = ['/static/components/css/test.css']
            js = ['/static/components/js/test.js']

in template/components/test.html :

    <div>
        mykwarg = {{ mykwarg }}
        <br/>
        myarg = {{ myarg }}
        <br/>
        {% if myflag %}
            my flag is true !
        {% else %}
            myflag is false !
        {% endif %}
        <br/>
        <div id="blockA">
        {{ nodelist_a }}
        </div>
        <div id="blockB">    
        {{ nodelist_b }}
        </div>
    </div>

in static/components/css/test.css:

    #blockA {
        border: 1px solid red;
        border-radius: 5px;
        padding: 10px;
        margin: 5px 10%;
        cursor: pointer;
    }
    #blockB {
        border: 1px solid blue;
        border-radius: 5px;
        padding: 10px;
        margin: 5px 10%;
        cursor: pointer;
    }

in static/components/js/test.js:
    document.addEventListener("DOMContentLoaded", function(event) { 
        document.getElementById("blockA").onclick = () => {
            alert('You click on block A')
        }
        document.getElementById("blockB").onclick = () => {
            alert('You click on block B')
        }
    })

and finally in your template:
    {% load component_tags example tryit %}
    <html>
    <head>
        {% component_dependencies %}
    </head>
    <body>
        {% mytest mykwarg='kwarg1' 'arg1' %}
            <p class="node-a">This is my first block: A</p>
        {% one %}
            <span class="node-after">This is my second block: B</span>
        {% endtest %}
    </body>
    </html>


Creation d'un composant: 
    Dans la class Tag, vous devez définir l'attribut name et la classe Media.
    Vous pouvez également rajouter l'attribut options.

    Dans options vous pouvez déclarer des Arguments, KeywordArguments, des Flags et des blocks.

    Les Arguments doivent avoir un paramètre name. Pluseurs autres paramètres peuvent être ajoutés:
        default: la valeur par défaut (par défaut: None)
        required: si l'Argument et requit (par défaut: True)
        resolve: si l'argument utilise le contexte pour determiner sa valeur (par défaut: True)
        value_class: classe de component_tags.values définissant le type (par défaut Value)

    Les KeywordArgument ont un paramètre supplémentaire:
        choices: une liste de valeurs que peut prendre la valeur du KeywordArgument (pas d'influence par defaut)
        value_class est inutile si choices est utilisé.

    Les Flag n'ont comme seul paramètre: name

    Les blocks sont une liste de tupple dont:
        - la 1ère valeur est le nom de votre balise 
        - la 2ème valeur est le nom de la valeur dans le contexte de la template de votre composant


    Les classes Values permettent de définir le type de vos Argument et KeywordArgument:
        Value: tout les types de valeurs
        StringValue: cast en string
        StrictStringValue: doit être une string
        IntegerValue: cast en int
        BooleanValue: cast en boolean
        FloatValue: cast en float
        IterableValue: doit être itérable
        ListValue: doit être une ListValue
        DictValue: doit être un dictionnaire

3. Utilisation dans la template:
    Si vous avez un composant qui a pour nom 'mytest'
    et que dans les options vous ayez: 
        Argument(name='myarg'),
        Argument(name='myarg2'),
        KeywordArgument(name='mykwarg', default=False),
        KeywordArgument(name='mykwarg2', default=False),
        Flag(name='myflag'),
        Flag(name='myflag2'),

    Et que vous souhaitez avoir pour votre composant:
        - myarg = 42
        - myarg2 = 64
        - mykwarg = 'foo'
        - mykwarg2 = 'bar'
        - myflag = True
        - myflag2 = False

    Vous pourriez aussi bien écrire dans votre template:
        {% mytest 42 64 mykwarg='foo' mykwarg='bar' myflag=True myflag2=False %}
        {% mytest 42 64 mykwarg='foo' mykwarg='bar' myflag %}
        {% mytest 42 64 myflag2=False mykwarg='bar' myflag mykwarg='foo' %}

    mais si vous écrivez:
        {% mytest 64 42 %}
        
    vous aurais:
        - myarg = 64
        - myarg2 = 42