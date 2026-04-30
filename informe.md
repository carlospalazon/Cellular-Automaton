<style>
/* Estils globals del document */
body {
  font-family: Helvetica, Arial, sans-serif;
  font-size: 9pt;
  text-align: justify;
  line-height: 1.4;
}

/* Paràgrafs justificats */
p {
  text-align: justify;
  font-size: 9pt;
}

/* Estils per a les llistes amb la mateixa mida que el text normal */
ul, ol, code {
  font-size: 9pt;
  line-height: 1.4;
}

li {
  font-size: 9pt;
  line-height: 1.4;
}

/* Títols més petits */
h1 {
  font-size: 13pt;
  text-align: left;
}

h2 {
  font-size: 12pt;
  text-align: left;
  font-weight: bold;
}

h3 {
  font-size: 11pt;
  text-align: left;
  font-weight: bold;
}

h4 {
  font-size: 9pt;
  text-align: left;
}

h5{
  font-size: 9pt;
  text-align: left;
  text-decoration: underline;
}

/* CORRECCIONS PER A BLOCS DE CODI */
pre {
  max-width: 100%;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
  background-color: #f5f5f5;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 3px;
  font-size: 8pt;
  line-height: 1.4;
  min-width: 0;
}

code {
  overflow-wrap: break-word;
  word-wrap: break-word;
  word-break: break-word;
  white-space: pre-wrap;
}

/* Contenidor principal */
.image-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;       /* Espai entre imatges */
  margin-top: 1rem;
  margin-bottom: 1rem;
  align-items: flex-start;
  width: 100%;
}

/* MODIFICAT: Reduïm la base (flex-basis) a 180px perquè hi capiguin 3 en una fila */
.image-column {
  flex: 1 1 180px; /* Abans 280px. Amb 180px, 3 imatges sumen ~540px + marges, que hi cap perfecte */
  max-width: 320px; /* Mida màxima per evitar que es facin gegants si n'hi ha poques */
  display: flex;
  flex-direction: column;
  align-items: center;
  box-sizing: border-box;
}

/* Regla específica: Si només hi ha UNA imatge, la deixem ser més gran */
.image-row:has(.image-column:only-child) .image-column {
  max-width: 480px;
  flex: 0 1 auto;
}

/* Imatges */
.image-column img {
  width: 100%;
  max-height: 280px; /* Limitem l'alçada */
  height: auto;
  display: block;
  object-fit: contain;
}

/* Peu de foto */
.image-column .caption {
  margin-top: 0.5rem;
  font-size: 8pt;
  text-align: center;
  color: #555;
  width: 100%;
}

/* ============================================
    CONTENIDOR GRID 2x2 PER A IMATGES
    ============================================ */
.image-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.8rem;
  margin-top: 1rem;
  margin-bottom: 1rem;
  width: 100%;
  max-width: 720px;
  margin-left: auto;
  margin-right: auto;
}

/* Cada cel·la del grid */
.image-grid .grid-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  box-sizing: border-box;
}

/* Imatges dins del grid 2x2 */
.image-grid .grid-item img {
  width: 100%;
  max-width: 360px;
  max-height: 320px;
  height: auto;
  display: block;
  object-fit: contain;
}

/* Peu de foto per a cada imatge del grid */
.image-grid .grid-item .caption {
  margin-top: 0.5rem;
  font-size: 8pt;
  text-align: center;
  color: #555;
  width: 100%;
}

/* Peu de figura general (opcional, per sota de tot el grid) */
.image-grid-caption {
  margin-top: 0.8rem;
  font-size: 8pt;
  text-align: center;
  color: #555;
  font-style: italic;
}

/* Estil per a la separació de pàgines en PDF */
.page-break {
  page-break-before: always;
  break-before: page;
}

/* Bloc imatge-esquerra / text-dreta */
.media-row {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
  margin: 1rem 0;
  min-width: 0;
}

.media-image {
  flex: 0 0 38%;
  max-width: 240px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.media-image img {
  width: 100%;
  height: auto;
  display: block;
}

.media-image .caption {
  margin-top: 0.5rem;
  font-size: 8pt;
  text-align: center;
  color: #555;
}

.media-text {
  flex: 1 1 0;
  min-width: 240px;
}

/* ============================================
    CONTENIDOR DE TAULES AMB PEU DE TAULA
    ============================================ */
.table-container {
  width: 100%;
  margin: 1.5rem 0;
  overflow-x: auto;
  page-break-inside: avoid;
}

/* Estils per a les taules */
.table-container table {
  width: 100%;
  max-width: 100%;
  border-collapse: collapse;
  font-size: 7pt;
  margin: 0 auto;
  background-color: #fff;
}

/* Capçalera de taula */
.table-container thead {
  background-color: #e0e0e0;
  font-weight: bold;
}

.table-container th {
  padding: 8px 6px;
  text-align: center;
  border: 1px solid #888;
  font-size: 7pt;
}

/* Files de dades */
.table-container td {
  padding: 6px 5px;
  text-align: center;
  border: 1px solid #aaa;
  font-size: 7pt;
}

.table-container td code {
  font-size: 7pt;
}

/* Files alternades (zebra striping) */
.table-container tbody tr:nth-child(even) {
  background-color: #f5f5f5;
}

/* Peu de taula (caption) */
.table-container .table-caption {
  margin-top: 0.5rem;
  font-size: 8pt;
  text-align: center;
  color: #555;
  font-style: italic;
}

/* Estil alternatiu: caption sobre la taula */
.table-container .table-title {
  margin-bottom: 0.5rem;
  font-size: 9pt;
  text-align: center;
  font-weight: bold;
  color: #333;
}

/* Millores per a impressió/PDF */
@media print {
  .table-container {
    page-break-inside: avoid;
  }

  .table-container table {
    border: 1px solid #000;
  }

  .table-container th,
  .table-container td {
    border: 1px solid #666;
  }

  .image-column {
    page-break-inside: avoid;
  }

  /* Límits més restrictius per a PDF */
  .image-column img {
    max-height: 280px;
  }

  .image-row:has(.image-column:only-child) .image-column img {
    max-height: 360px;
  }

  /* Grid 2x2 en impressió */
  .image-grid {
    page-break-inside: avoid;
  }

  .image-grid .grid-item img {
    max-height: 280px;
  }

  pre {
    page-break-inside: avoid;
    overflow: visible;
    white-space: pre-wrap;
  }
}

@page {
  @bottom-center {
    content: "Pàgina " counter(page) " de " counter(pages);
    font-size: 8pt;
    color: #555;
    font-family: Helvetica, Arial, sans-serif;
  }
}
</style>

# 0. Índex

# 1. Introducció

Els autòmats cel·lulars constitueixen una eina fonamental en l’estudi de sistemes complexos, ja que permeten modelitzar com comportaments globals poden emergir a partir de regles locals molt simples. En particular, els autòmats cel·lulars elementals definits per *Stephen Wolfram* representen un dels casos més bàsics i, alhora, més il·lustratius d’aquest tipus de sistemes, on una graella unidimensional de cel·les binàries evoluciona en el temps segons un conjunt finit de regles.

L’objectiu de la primera part d’aquesta pràctica és implementar computacionalment aquests autòmats cel·lulars utilitzant un llenguatge de programació (en aquest cas, Python), permetent la simulació de diferents regles de Wolfram i la seva visualització temporal. A més, s’introdueix el concepte de coarse-graining o “gra gruixut”, aplicant una reducció de resolució amb factor K=2, amb la finalitat d’analitzar si les propietats macroscòpiques del sistema es conserven malgrat la pèrdua d’informació microscòpica. Aquest procés permet explorar la robustesa del comportament global i la seva dependència respecte als detalls locals.

En la segona part es desenvolupa un model d’autòmat cel·lular bidimensional per simular la propagació d’un incendi forestal mitjançant un esquema multi-capa del tipus $m:n-CA^k$. El sistema es construeix a partir de dades ambientals que inclouen, com a mínim, dues capes principals: humitat i vegetació.

La vegetació representa el temps necessari perquè una cel·la es consumeixi completament pel foc, mentre que la humitat introdueix un retard inicial que impedeix o dificulta l’encesa. A partir de la interacció entre aquestes capes i l’estat de les cel·les veïnes, es modelitza la propagació del foc mitjançant una capa d’estats amb tres fases: pendent de cremar-se, en combustió i cremat.

Addicionalment, s’incorpora una capa vectorial de vent que introdueix una direcció preferent en la propagació de l’incendi, modificant la probabilitat d’extensió del foc segons l’orientació espacial. Això permet aproximar de manera més realista el comportament anisotròpic dels incendis forestals.

# 2. Autòmat cel·lular de Wolfram

## 2.1. Objectius i metodologia

En aquesta primera part de la pràctica es desenvolupa una implementació en Python d’un autòmat cel·lular elemental basat en les regles de Wolfram. Aquests sistemes consisteixen en una graella unidimensional de cel·les binàries que evolucionen en el temps segons una regla local que depèn de l’estat de la cel·la i dels seus veïns immediats. Tot i la simplicitat de les regles, aquests models són capaços de generar comportaments altament diversos i, en alguns casos, complexos.

L’objectiu principal d’aquesta part és estudiar l’evolució temporal de diferents regles representatives i comparar el comportament del sistema original amb una versió simplificada mitjançant un procés de *coarse-graining* amb factor $K=2$. Aquest procés consisteix en una reducció de resolució espacial del sistema, agrupant cel·les en blocs, amb la finalitat d’analitzar si les propietats globals del sistema es mantenen o canvien quan es perd informació microscòpica.

Per a l’estudi s’han seleccionat diverses regles representatives del conjunt de 256 possibles regles de Wolfram. En concret, s’han analitzat les regles 0, 30, 90 i 110, ja que permeten observar diferents classes de comportament: des d’estats completament estacionaris (regla 0), passant per dinàmiques caòtiques (regla 30), estructures fractals (regla 90), fins a comportaments complexos amb potencial universal (regla 110). Aquesta selecció permet explorar una varietat significativa de dinàmiques dins del mateix marc formal.

Pel que fa a les condicions de contorn, s’ha adoptat una condició periòdica, en la qual la graella es tracta com un sistema tancat amb topologia circular. Això implica que la primera i l’última cel·la són veïnes, evitant així efectes artificials als extrems del sistema i garantint una evolució homogènia al llarg de tota la graella.

Finalment, mitjançant la comparació entre el sistema original i la seva versió amb coarse-graining, es pretén analitzar fins a quin punt les dinàmiques observades són robustes davant canvis d’escala, contribuint així a l’estudi del comportament emergent en sistemes complexos.

--- 

## 2.2. Sistema original

En aquesta figura es presenta la comparació de l’evolució temporal de quatre autòmats cel·lulars elementals corresponents a les regles 0, 30, 90 i 110. Cada subfigura mostra la dinàmica espaciotemporal del sistema a partir d’una condició inicial amb una única cel·la activa, permetent observar les diferències qualitatives entre comportaments generats per regles locals diferents.

<img src="/sessio1/wolfram_multiple_rules.png" alt="descripció" width="1500">

- **Regla 0:** S’observa que el sistema convergeix immediatament cap a un estat completament buit, on totes les cel·les adopten el valor 0. Aquest comportament correspon a una dinàmica trivial de classe 1, caracteritzada per l’absència de propagació i la desaparició completa de qualsevol estructura inicial. El sistema entra ràpidament en un estat absorbent estacionari.

- **Regla 30:** El sistema presenta una dinàmica clarament caòtica i aperiòdica. A partir de la condició inicial amb una única cel·la activa, el patró s'expandeix de manera asimètrica, sense mostrar cap estructura regular ni periodicitat detectable. El costat esquerre mostra una aparença aleatòria, mentre que el costat dret presenta una franja de progressió més regular. Aquest comportament és característic de la classe 3 de Wolfram, on la dinàmica és sensible a les condicions inicials i genera patrons que recorden seqüències pseudoaleatòries. De fet, Wolfram va proposar la Regla 30 com a generador de nombres pseudoaleatoris per a aplicacions computacionals.

- **Regla 90:** S’observa la formació d’un patró fractal altament estructurat amb simetria triangular. Aquest comportament és determinista i regular, i genera una estructura global auto-similar. Correspon a una dinàmica de classe 2, on el sistema no és caòtic però tampoc convergeix a un estat fix, sinó que produeix patrons periòdics i geomètricament estructurats.

- **Regla 110:** La dinàmica presenta una combinació de regularitat local i complexitat global. Es poden observar estructures persistents que es propaguen i interactuen, conegudes com a “gliders”, juntament amb zones més irregulars. Aquest comportament és característic de la classe 4, situada entre ordre i caos, i és especialment rellevant pel seu potencial de computació universal.

Els resultats mostren que petites variacions en les regles locals generen comportaments globalment molt diferents, des de dinàmiques trivials fins a estructures complexes. Això posa de manifest el caràcter emergent dels autòmats cel·lulars i la seva capacitat per generar complexitat a partir de regles extremadament simples.

## 2.3. Comparació amb coarse-graining

En aquesta secció es compara el comportament dels autòmats cel·lulars originals amb la seva versió simplificada mitjançant un procés de coarse-graining amb factor $K=2$. Aquest procediment consisteix en agrupar blocs de cel·les per reduir la resolució espacial del sistema, permetent analitzar la robustesa de les estructures emergents davant una pèrdua d’informació microscòpica.

<div style="text-align: center;">
  <img src="/sessio1/wolfram_rule30_comparison.png" alt="descripció" width="500">
</div>

En el cas de la Regla 30, el sistema original mostra una dinàmica clarament caòtica, amb una expansió irregular de patrons que no presenta simetria ni periodicitat. Aquesta complexitat es manté, en termes qualitatius, en la versió coarse-grained, tot i que es produeix una pèrdua notable de detall.

El sistema reduït conserva la sensació general de desordre i imprevisibilitat, però les fluctuacions fines desapareixen parcialment, donant lloc a una representació més suau de la dinàmica. Això indica que el comportament caòtic és robust a canvis d’escala, encara que la informació microscòpica sigui parcialment eliminada.

<div style="text-align: center;">
  <img src="/sessio1/wolfram_rule90_comparison.png" alt="descripció" width="500">
</div>

Per a la Regla 90, el sistema original genera una estructura altament ordenada amb forma triangular i simetria fractal, característica de dinàmiques deterministes i auto-similars. Aquesta estructura es manté sorprenentment ben preservada en el procés de coarse-graining.

Tot i la reducció de resolució, la forma global del patró continua sent clarament recognoscible, indicant que la informació essencial del sistema es troba en l’estructura macroscòpica i no en els detalls locals. Això reforça la naturalesa fractal i auto-similar de la Regla 90.

<div style="text-align: center;">
  <img src="/sessio1/wolfram_rule110_comparison.png" alt="Comparació Regla 110 original i coarse-grain" width="500">
</div>

En el cas de la Regla 110, el sistema original exhibeix una dinàmica molt característica de la classe 4: es poden observar estructures localitzades i periòdiques ("gliders") que es propaguen cap a l'esquerra i interactuen entre si, sobre un fons de cert desordre. El front d'expansió té una inclinació marcada cap a l'esquerra, cosa que reflecteix l'asimetria intrínseca de la regla. La coexistència de zones regulars i zones de complexitat local és el tret definitori d'aquest comportament, i el que fa la Regla 110 especialment rellevant: s'ha demostrat que és Turing-completa, és a dir, capaç de realitzar qualsevol càlcul computable.
En la versió amb coarse-graining, les estructures principals es mantenen recognoscibles. El front d'expansió inclinat i les zones de densitat diferenciada es conserven clarament, tot i que els "gliders" individuals queden fusionats i la textura interna es simplifica notablement. A diferència de la Regla 30, on el coarse-graining preserva principalment el caràcter caòtic global, en la Regla 110 la reducció de resolució conserva millor l'estructura macroscòpica perquè les regularitats persistents del sistema operen a una escala espaciotemporal superior a la de dos píxels. No obstant això, la complexitat fina de les interaccions entre gliders es perd irreversiblement, cosa que indica que una part essencial de la riquesa computacional de la Regla 110 resideix precisament en els detalls microscòpics.

## 2.4. Conclusions

En conjunt, l'estudi dels quatre autòmats cel·lulars elementals i la seva versió simplificada per coarse-graining posa en evidència tres conclusions principals. En primer lloc, regles locals extremadament senzilles poden generar comportaments globals de naturalesa molt diversa, des de l'extinció immediata (Regla 0) fins a la computació universal (Regla 110), passant per el caos (Regla 30) i les estructures fractals (Regla 90). En segon lloc, el procés de coarse-graining preserva les propietats qualitatives macroscòpiques del sistema en tots els casos estudiats, tot i que amb diferent fidelitat segons la classe dinàmica: les estructures fractals de la Regla 90 i el caos de la Regla 30 es conserven millor que els detalls locals de la Regla 110. En tercer lloc, la robustesa del comportament emergent davant canvis d'escala suggereix que les propietats globals dels autòmats cel·lulars no depenen únicament dels detalls microscòpics, sinó que emergen de patrons d'interacció d'abast superior.

# 3. Modelització incendi forestal

## 3.1. Objectius i metodologia

En aquesta segona part de la pràctica es desenvolupa un simulador d'incendi forestal basat en un autòmat cel·lular bidimensional. L'idea principal és que cada cel·la de la graella representa una petita parcel·la de terreny, i que el foc es propaga de cel·la en cel·la seguint unes regles senzilles que depenen de les característiques del terreny: quanta vegetació hi ha i com d'humida està.

L'objectiu és que la simulació sigui el més realista possible. Per això, el model treballa amb dues capes de dades ambientals (vegetació i humitat) que interactuen entre elles, i una tercera capa que registra en quin estat de combustió es troba cada zona del terreny en cada moment.

Les dades de les capes es poden carregar des de fitxers externs en format IDRISI32 o bé generar-se automàticament seguint patrons que imiten els que es poden trobar a la natura, tal com s'explica més endavant.

## 3.2. Les tres capes del model

El model s'organitza en tres capes que evolucionen conjuntament en cada pas de temps, on cada pas equival a una hora:

**L1 – Vegetació:** Indica quantes hores triga a cremar-se la vegetació de cada cel·la. Una zona de bosc dens triga molt més (fins a 20 hores) que una zona de prat o herba seca (1–3 hores). Si una cel·la no té vegetació, el foc no s'hi pot propagar.

**L2 – Humitat:** Indica quantes hores ha d'esperar el foc abans de poder encendre una cel·la. Una zona propera a un riu o llac pot tenir tanta humitat que el foc trigarà moltes hores a iniciar-se, mentre que una zona seca s'encendrà de seguida.

**L3 – Propagació:** Registra l'estat del foc a cada cel·la en cada moment. Cada cel·la pot estar en un d'aquests quatre estats:

| Valor | Estat | Significat |
|-------|-------|------------|
| `0` | Pendent | Encara no ha rebut foc |
| `1` | Eixugant | Ha rebut calor d'una cel·la veïna i s'està secant |
| `2` | Cremant | Està en flames i pot encendre les cel·les del voltant |
| `3` | Cremat | S'ha consumit completament |

<div class="image-row">
  <div class="image-column">
    <img src="/sessio2/capa_humitat.png" alt="Descripció 1">
    <div class="caption">Figura 1. Capa de la humitat</div>
  </div>
  <div class="image-column">
    <img src="/sessio2/capa_vegetació.png" alt="Descripció 2">
    <div class="caption">Figura 2. Capa de la vegetació</div>
  </div>
</div>


## 3.3. Com es propaga el foc

En cada pas de temps, el sistema comprova totes les cel·les i aplica les regles següents:

- Una cel·la **pendent** s'encén si té alguna cel·la veïna en flames. Si té humitat acumulada, primer passa per la fase d'eixugament; si no en té, s'encén directament.
- Una cel·la **eixugant** va perdent humitat hora a hora fins que s'esgota i comença a cremar.
- Una cel·la **cremant** va consumint la seva vegetació hora a hora fins que s'apaga i queda cremada.
- Una cel·la **cremada** ja no canvia d'estat.

Es pot configurar si el foc es propaga als 4 veïns més propers (amunt, avall, esquerra, dreta) o als 8 veïns en totes les direccions, incloent les diagonals.

## 3.4. Generació de les capes seguint patrons naturals

Per tal que la simulació sigui creïble, les capes de vegetació i humitat s'han generat imitant els patrons que es troben habitualment en terrenys naturals, en lloc d'usar valors aleatoris sense cap coherència espacial.

En la natura, la distribució de la vegetació i la humitat no és uniforme ni aleatòria: les valls acumulen més humitat que els turons, els rius i els llacs mantenen les zones properes més humides, i els boscos densos tendeixen a créixer en zones més protegides i amb més aigua. Per reproduir aquest comportament, la generació de les capes segueix tres etapes:

1. **Relleu del terreny:** Es genera un mapa d'elevació que imita la forma d'un terreny real, amb muntanyes, valls i planes. Les zones altes reben menys vegetació (roca, prat alpí) i les zones baixes n'acumulen més (bosc dens).

2. **Humitat del sòl:** La humitat és més alta a les valls i més baixa a les zones elevades i exposades. A més, s'hi afegeixen rius que segueixen el camí natural descendent pel terreny i llacs que s'ubiquen als punts més baixos, creant zones d'alta humitat al seu voltant.

3. **Vegetació:** A partir del relleu i la humitat, s'assigna a cada cel·la un tipus de vegetació coherent amb la seva posició: les zones seques i altes tenen arbust o herba, i les zones humides i baixes tenen bosc més dens i amb més hores de combustió.

El resultat és un terreny on les zones humides (riberes, valls) actuen com a barreres naturals que alenteixen el foc, i les zones seques (turons, sotabosc escàs) afavoreixen una propagació més ràpida, de manera molt similar al que s'observa en incendis reals.

## 3.5. Implementació

El simulador s'ha implementat completament en Python, fent servir `numpy` per gestionar les capes de dades i `matplotlib` per mostrar la simulació de manera visual i interactiva. La interfície permet controlar la simulació pas a pas o de manera automàtica, canviar la capa que es visualitza (propagació, vegetació o humitat) i iniciar focus d'ignició fent clic directament sobre la graella.

El programa s'executa des de la línia de comandes i accepta diverses opcions de configuració:

```bash
python incendi_forestal.py [--terrain {mediterranean,alpine,savanna,coastal}]
                           [--veg fitxer.rst --hum fitxer.rst]
                           [--rows N] [--cols M]
                           [--seed S]
                           [--neighborhood {moore,von_neumann}]
```