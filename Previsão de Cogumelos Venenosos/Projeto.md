Previsão de Cogumelos Venenosos

CONTEXTO

Em muitas culturas ao redor do mundo, a busca por cogumelos selvagens é uma atividade popular e gratificante. No entanto, esse hobby traz riscos significativos. Alguns cogumelos que parecem inofensivos podem ser altamente tóxicos, levando a consequências graves para a saúde se consumidos. Diferenciar entre cogumelos comestíveis e venenosos é uma habilidade com a qual até mesmo forrageadores experientes podem ter dificuldade.

Um cientista de dados teoriza que é possivel de desenvolver uma ferramenta para auxiliar os forrageadores a identificar cogumelos com segurança. 


DESAFIO

Seu objetivo é criar um modelo preditivo que possa distinguir com precisão entre cogumelos venenosos e não venenosos com base em vários recursos, como formato do chapéu, cor, fixação das guelras e habitat.

•	Avaliação: Os envios são avaliados usando o coeficiente de correlação de Matthews (MCC). 
•	Arquivo de envio: Para cada linha de id no conjunto de teste, você deve prever a classe de destino, se a observação é comestivel (e) ou venenosa (p). O arquivo deve conter um cabeçalho e ter o seguinte formato:
Id	class
945	e
946	p
947	e

RECURSOS

O conjunto de dados contém informações sobre diferentes espécies de cogumelos, cada uma rotulada como venenosa ou não venenosa. Este conjunto de dados contém as seguintes colunas:

Attribute	Description	Possible Values
class	classification	edible=e, poisonous=p
cap-shape	Shape of the mushroom cap	bell=b, conical=c, convex=x, flat=f, knobbed=k, sunken=s
cap-surface	Surface texture of the mushroom cap	fibrous=f, grooves=g, scaly=y, smooth=s
cap-color	Color of the mushroom cap	brown=n, buff=b, cinnamon=c, gray=g, green=r, pink=p, purple=u, red=e, white=w, yellow=y
bruises?	Whether the mushroom bruises	bruises=t, no=f
odor	Odor of the mushroom	almond=a, anise=l, creosote=c, fishy=y, foul=f, musty=m, none=n, pungent=p, spicy=s
gill-attachment	How the gills are attached to the stem	attached=a, descending=d, free=f, notched=n
gill-spacing	Spacing between the gills	close=c, crowded=w, distant=d
gill-size	Size of the gills	broad=b, narrow=n
gill-color	Color of the gills	black=k, brown=n, buff=b, chocolate=h, gray=g, green=r, orange=o, pink=p, purple=u, red=e, white=w, yellow=y
stalk-shape	Shape of the stalk	enlarging=e, tapering=t
stalk-root	Root type of the stalk	bulbous=b, club=c, cup=u, equal=e, rhizomorphs=z, rooted=r, missing=?
stalk-surface-above-ring	Surface texture of the stalk above the ring	fibrous=f, scaly=y, silky=k, smooth=s
stalk-surface-below-ring	Surface texture of the stalk below the ring	fibrous=f, scaly=y, silky=k, smooth=s
stalk-color-above-ring	Color of the stalk above the ring	brown=n, buff=b, cinnamon=c, gray=g, orange=o, pink=p, red=e, white=w, yellow=y
stalk-color-below-ring	Color of the stalk below the ring	brown=n, buff=b, cinnamon=c, gray=g, orange=o, pink=p, red=e, white=w, yellow=y
veil-type	Type of veil covering the mushroom	partial=p, universal=u
veil-color	Color of the veil	brown=n, orange=o, white=w, yellow=y
ring-number	Number of rings on the mushroom stalk	none=n, one=o, two=t
ring-type	Type of ring on the mushroom stalk	cobwebby=c, evanescent=e, flaring=f, large=l, none=n, pendant=p, sheathing=s, zone=z
spore-print-color	Color of the spore print	black=k, brown=n, buff=b, chocolate=h, green=r, orange=o, purple=u, white=w, yellow=y
population	Population distribution of the mushroom	abundant=a, clustered=c, numerous=n, scattered=s, several=v, solitary=y
habitat	Habitat where the mushroom grows	grasses=g, leaves=l, meadows=m, paths=p, urban=u, waste=w, woods=d
