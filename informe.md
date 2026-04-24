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

- **Regla 30:** S’observa que el sistema convergeix immediatament cap a un estat completament buit, on totes les cel·les adopten el valor 0. Aquest comportament correspon a una dinàmica trivial de classe 1, caracteritzada per l’absència de propagació i la desaparició completa de qualsevol estructura inicial. El sistema entra ràpidament en un estat absorbent estacionari.

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


# 3. Modelització incendi forestal