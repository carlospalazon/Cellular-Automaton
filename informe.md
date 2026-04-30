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

En aquesta primera part de la pràctica es desenvolupa una implementació en Python d'un autòmat cel·lular elemental basat en les regles de Wolfram. Aquests sistemes consisteixen en una graella unidimensional de cel·les binàries que evolucionen en el temps segons una regla local que depèn de l'estat de la cel·la i dels seus veïns immediats. Tot i la simplicitat de les regles, aquests models són capaços de generar comportaments altament diversos i, en alguns casos, complexos.

L’objectiu principal d’aquesta part és estudiar l’evolució temporal de diferents regles representatives i comparar el comportament del sistema original amb una versió simplificada mitjançant un procés de *coarse-graining* amb factor $K=2$. Aquest procés consisteix en una reducció de resolució espacial del sistema, agrupant cel·les en blocs, amb la finalitat d’analitzar si les propietats globals del sistema es mantenen o canvien quan es perd informació microscòpica.

Per a l’estudi s’han seleccionat diverses regles representatives del conjunt de 256 possibles regles de Wolfram. En concret, s’han analitzat les regles 0, 30, 90 i 110, ja que permeten observar diferents classes de comportament: des d’estats completament estacionaris (regla 0), passant per dinàmiques caòtiques (regla 30), estructures fractals (regla 90), fins a comportaments complexos amb potencial universal (regla 110). Aquesta selecció permet explorar una varietat significativa de dinàmiques dins del mateix marc formal.

Pel que fa a les condicions experimentals, s'han adoptat configuracions diferenciades segons la regla estudiada. Les regles 0, 30 i 110 s'analitzen amb condició inicial de cel·la única activa al centre (single) i condicions de contorn periòdiques, en les quals la primera i l'última cel·la són veïnes, evitant efectes artificials als extrems. La regla 90, en canvi, s'estudia amb condició inicial aleatòria i frontera zero —és a dir, cel·les als extrems fixades al valor 0— per tal de posar en evidència la seva dinàmica d'interferència constructiva i destructiva: amb una única cel·la activa, la Regla 90 generaria simplement el triangle de Sierpiński clàssic, un resultat àmpliament conegut que no permet observar el comportament emergent sobre un fons dens ni la jerarquia de triangles invertits característica de la superposició d'ones en sistemes XOR.

Finalment, mitjançant la comparació entre cada sistema original i la seva versió amb coarse-graining, es pretén analitzar fins a quin punt les dinàmiques observades són robustes davant canvis d'escala, contribuint així a l'estudi del comportament emergent en sistemes complexos.

--- 

## 2.2. Sistema original

En aquesta secció es presenta l'anàlisi detallada de l'evolució temporal de quatre autòmats cel·lulars elementals de Wolfram: les regles 0, 30, 90 i 110. Cada sistema parteix d'una condició inicial amb una única cel·la activa (single) i condicions de contorn periòdiques, amb l'excepció de la Regla 90, que s'analitza amb condició inicial aleatòria i frontera zero. La representació espaciotemporal codifica en negre les cel·les amb valor 1 i en blanc les de valor 0, amb el temps avançant de dalt a baix i la posició espacial a l'eix horitzontal.

<img src="/sessio1/wolfram_multiple_rules.png" alt="descripció" width="1500">

- **Regla 0:** El sistema convergeix de manera immediata cap a l'estat absorbent de valor zero. Independentment de la configuració inicial, la regla mapeja totes les combinacions de veïnats al valor 0, de manera que l'únic atractor del sistema és l'estat buit. Això correspon a la classe 1 de Wolfram: dinàmica completament trivial, sense propagació ni emergència de cap estructura. L'extinció es produeix en un únic pas temporal, cosa que posa de manifest que la regla no conté cap mecanisme de manteniment o propagació de l'activitat.

- **Regla 30:** El sistema exhibeix una expansió simètrica en forma de con a partir de la cel·la inicial activa, delimitada pels fronts de propagació màxima a esquerra i dreta. Tot i que el contorn extern del patró és perfectament regular —determinat per la velocitat de propagació unitària de la regla—, l'interior del con presenta una dinàmica clarament caòtica i aperiòdica, sense cap estructura repetitiva ni eix de simetria intern. Les columnes individuals no mostren periodicitat detectable, i la sensibilitat a les condicions inicials és màxima: una única pertorbació microscòpica propaga divergències que s'estenen ràpidament per tot el sistema. Aquest comportament és característic de la classe 3 de Wolfram. De fet, la columna central de la Regla 30 genera una seqüència binària que supera molts tests d'aleatorietat estadística, raó per la qual Wolfram la va proposar com a base per a generadors de nombres pseudoaleatoris d'alta qualitat.

- **Regla 90:** Amb condició inicial aleatòria i frontera zero, el sistema no exhibeix el triangle fractal de Sierpiński clàssic associat a la condició single, sinó un comportament curiós i revelador de la dinàmica XOR intrínseca d'aquesta regla. A partir d'un estat inicial dens i desordenat, el sistema evoluciona generant progressivament triangles blancs invertits —zones de cel·les inactives— que emergeixen i creixen de manera jeràrquica sobre el fons actiu. Cada triangle blanc és el resultat de la interferència destructiva entre ones que es propagen en sentits oposats: quan dues ones de la mateixa fase es troben, s'anul·len mutualment. L'estructura resultant és una versió negativa del triangle de Sierpiński, amb la mateixa auto-similaritat però invertida cromàticament. La distribució dels buits segueix una jerarquia d'escales ben definida, amb triangles de mides decreixents que es repeteixen a totes les escales accessibles del sistema. Això és consistent amb la naturalesa lineal de la Regla 90 (equivalent a un XOR dels veïns), que permet la superposició de solucions i genera comportaments que recorden la difracció d'ones en un medi discret. La frontera zero imposa condicions de reflectivitat que interaccionen amb la dinàmica interna, contribuint a la regularitat de les estructures emergents.

- **Regla 110:** El sistema genera un patró d'alta complexitat que combina zones de regularitat local amb irregularitat global. El front de propagació presenta una asimetria marcada: l'expansió cap a l'esquerra és ràpida i abrupte, mentre que la propagació cap a la dreta és molt més lenta, reflectint la asimetria intrínseca de la taula de la regla. L'interior del con d'activació mostra l'existència d'estructures localitzades i persistents —conegudes com a gliders— que es desplacen periòdicament dins del fons quasi-periòdic. Aquestes estructures interactuen entre si de manera no trivial, col·lidint i generant noves estructures o destruint-se. La coexistència d'un fons amb estructura quasi-periòdica i d'objectes localitzats en moviment és la signatura característica de la classe 4 de Wolfram. La Regla 110 és especialment rellevant des del punt de vista computacional: Matthew Cook va demostrar l'any 2004 que és Turing-completa, és a dir, que pot simular qualsevol màquina de Turing i, per tant, realitzar qualsevol càlcul computable. Això la converteix en un dels sistemes computacionals més simples coneguts amb capacitat de computació universal.


Els resultats en conjunt il·lustren de manera contundent com petites variacions en la taula de transició local, que en tots els casos consta de només 8 entrades binàries, poden donar lloc a comportaments globals qualitativament molt dispars. Aquesta diversitat emergent constitueix un dels arguments centrals a favor de l'estudi dels autòmats cel·lulars com a models de sistemes complexos.

## 2.3. Comparació amb coarse-graining

El procés de *coarse-graining* o gra gruixut amb factor $K=2$ consisteix a substituir cada bloc de $2×1$ cel·les contigües per una única cel·la, assignant-li el valor 1 si la majoria de les cel·les del bloc estan actives (o bé per majoria, o bé per qualsevol altre criteri de fusió). El resultat és una representació de la dinàmica a una resolució espacial inferior, on cada cel·la de la nova graella condensa la informació de dues cel·les originals. L'objectiu d'aquesta anàlisi és determinar en quina mesura les propietats qualitatives i estructurals del sistema es conserven quan s'elimina informació a escala microscòpica, cosa que permet avaluar la robustesa del comportament emergent respecte als detalls locals.

<div style="text-align: center;">
  <img src="/sessio1/wolfram_rule30_comparison.png" alt="descripció" width="500">
</div>

En el sistema original, la Regla 30 exhibeix el con d'expansió simètric amb interior caòtic descrit anteriorment. En la versió coarse-grained (50×40), la forma global triangular es preserva perfectament: els fronts de propagació esquerre i dret continuen essent clarament identificables i mantenen la mateixa inclinació. Això indica que la velocitat de propagació màxima —una propietat macroscòpica del sistema— és robusta davant la reducció d'escala.

Pel que fa a l'interior del con, el caràcter desordenat es manté qualitativament: no apareix cap estructura periòdica ni simetria que no fos present en l'original. No obstant això, la textura del soroll canvia: les fluctuacions a escala d'un sol píxel desapareixen, donant lloc a una representació més granular on els patrons mínims visibles ocupen ara 2 unitats espacials. Es pot observar que certes correlacions de curt abast del sistema original —invisibles a escala fina— emergeixen lleugerament en la versió reduïda com a zones de densitat lleugerament diferenciada, sense arribar a constituir estructures coherents.

En conjunt, la Regla 30 és el cas on el coarse-graining preserva millor el comportament qualitatiu, precisament perquè el caos és una propietat global i no depèn dels detalls a escala de cel·la individual. La imprevisibilitat i la manca de estructura persistent són robustes a la reducció d'escala.

<div style="text-align: center;">
  <img src="/sessio1/wolfram_rule90_comparison.png" alt="descripció" width="500">
</div>

En el sistema original amb condició inicial aleatòria, s'observen triangles blancs invertits emergint sobre el fons actiu. En la versió coarse-grained, aquesta estructura es preserva parcialment però de manera inequívoca: els triangles invertits de gran mida —aquells que ocupen un nombre significatiu de cel·les en l'original— continuen essent identificables en la versió reduïda. Les seves vèrtexs, arestes i la jerarquia entre triangles de diferent mida es mantenen recognoscibles.

En canvi, els triangles de menor escala —aquells l'amplada dels quals en l'original era de l'ordre de 2–4 cel·les— desapareixen completament en la versió coarse-grained, absorbits per la fusió de blocs. Això és consistent amb el caràcter multi-escala de la dinàmica de la Regla 90: les estructures que operen a una escala igual o inferior al factor de reducció es perden irreversiblement, mentre que les estructures d'escala superior es conserven. Aquesta observació confirma la natura fractal de la Regla 90: el coarse-graining actua com un filtre passa-baix que elimina les components d'alta freqüència espacial, però respecta les components de baixa freqüència que constitueixen l'esquelet de l'estructura.

Un aspecte notable és que la versió reduïda sembla, en alguns sectors, menys ordenada que l'original, en contra del que podria esperar-se intuïtivament. Això es deu al fet que la condició inicial aleatòria introdueix correlacions de fase que la regla XOR propaga de manera coherent a l'escala original, però que el coarse-graining trenca parcialment en fusionar cel·les de fases potencialment oposades. El resultat és una lleugera degradació de la coherència estructural a les zones de menor densitat de triangles.

<div style="text-align: center;">
  <img src="/sessio1/wolfram_rule110_comparison.png" alt="Comparació Regla 110 original i coarse-grain" width="500">
</div>

La Regla 110 representa el cas analíticament més ric i, alhora, el que millor il·lustra els límits del coarse-graining com a tècnica de reducció. En el sistema original, el front inclinat d'expansió i la distribució espacial de les zones actives constitueixen propietats macroscòpiques clarament visibles. En la versió coarse-grained, el front d'expansió inclinat es conserva amb gran fidelitat: la inclinació, la velocitat de propagació i la distinció entre la zona activa i la zona inactiva (fons blanc) es mantenen de manera inequívoca. Fins i tot l'aparició secundària d'activitat a l'extrem dret del sistema —producte de la condició de frontera periòdica— és visible en la versió reduïda.

No obstant això, les estructures internes de petit abast —els gliders individuals i les seves interaccions— es perden gairebé completament. En l'original, es poden identificar a simple vista objectes localitzats de mida 3–6 cel·les que es desplacen periòdicament; en la versió coarse-grained, aquests objectes queden fusionats amb el fons o entre si, donant lloc a taques irregulars que no permeten identificar trajectòries ni periodicitats. Això és especialment significatiu des del punt de vista computacional: si la capacitat de computació universal de la Regla 110 rau en la interacció precisa entre gliders, la versió coarse-grained perd precisament la informació necessària per a dur a terme aquesta computació.

En termes d'informació, la Regla 110 és el sistema on el coarse-graining té un impacte funcional més gran: tot i que la representació macroscòpica és fidelment preservada, la pèrdua d'informació a escala local és funcionalment irreversible i destrueix les propietats computacionals del sistema. Això contrasta amb la Regla 30, on la pèrdua d'informació microscòpica no altera substancialment cap propietat global rellevant, i amb la Regla 90, on la jerarquia multi-escala permet una preservació parcial i graduada de l'estructura.

## 2.4. Conclusions

En conjunt, els resultats mostren que la robustesa del comportament davant el coarse-graining és inversament proporcional a la complexitat funcional del sistema: les dinàmiques més simples (caos uniforme) es preserven millor, mentre que les dinàmiques computacionalment riques (classe 4) pateixen les pèrdues d'informació més significatives. Això suggereix que la complexitat computacional requereix precisament la informació que el coarse-graining elimina, i que els sistemes de classe 4 operen a l'escala mínima de resolució possible.

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


# 4. Ús de la IA

L’ús d’eines d’intel·ligència artificial generativa en aquest treball s’ha integrat de manera sistemàtica dins del flux de treball, seguint criteris de rigor acadèmic i d’acord amb les directrius de la Universitat Politècnica de Catalunya. En concret, s’ha utilitzat l’assistent Claude com a eina de suport tant en el desenvolupament del codi com en la redacció de l’informe.

En l’àmbit de la implementació, la intel·ligència artificial ha tingut un paper central en la generació del codi. Aquest ús s’ha incorporat com una part activa del procés de desenvolupament, permetent explorar solucions de manera ràpida, prototipar funcionalitats i resoldre problemes tècnics amb major eficiència. Això ha contribuït significativament a agilitzar el flux de treball, reduint el temps necessari per implementar estructures bàsiques i facilitant la iteració sobre diferents aproximacions. No obstant això, aquest procés no ha estat en cap cas automàtic ni delegat completament a la IA: tot el codi generat ha estat revisat, comprès i adaptat manualment. Aquesta revisió ha inclòs la validació del funcionament, la detecció i correcció d’errors, així com l’ajust de les solucions a les necessitats específiques del model desenvolupat. En aquest sentit, la IA ha actuat com a eina de generació i acceleració, mentre que el control, la integració i la coherència global del sistema han estat responsabilitat directa dels autors.

Pel que fa a la redacció de l’informe, la IA s’ha utilitzat com a suport per millorar la qualitat lingüística i expositiva del text. En particular, ha contribuït a reformular fragments, estructurar millor les explicacions i mantenir un to acadèmic coherent al llarg del document. Aquest ús ha permès obtenir una redacció més clara i precisa, facilitant la comunicació dels conceptes treballats. Tanmateix, el contingut conceptual, l’organització del treball, la selecció dels resultats i la seva interpretació han estat definits prèviament i revisats de manera crítica, assegurant que el document reflecteixi fidelment el procés de treball realitzat.

Cal destacar que tota la informació generada amb suport d’intel·ligència artificial ha estat sotmesa a un procés de supervisió humana rigorós. Aquesta supervisió ha estat essencial per garantir la correcció tècnica del codi, la coherència de les explicacions i l’absència d’errors o interpretacions incorrectes derivades de les limitacions pròpies d’aquestes eines. Així mateix, s’ha mantingut en tot moment el control sobre el contingut final, evitant una dependència acrítica de la IA.

Finalment, l’ús d’aquestes eines s’ha limitat a informació de caràcter tècnic i general, sense incloure dades personals ni continguts sensibles, respectant així els principis de privacitat i ús responsable. En conjunt, la intel·ligència artificial s’ha utilitzat com una eina d’assistència avançada integrada dins del procés de treball, que ha permès augmentar l’eficiència i la qualitat del desenvolupament, sense substituir en cap cas el procés de raonament, anàlisi i validació propi. Els autors assumeixen íntegrament la responsabilitat del contingut final del treball, així com de la seva validesa i qualitat.