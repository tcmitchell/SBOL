import os
import sys
import unittest

import rdflib

import sbol2

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
CRISPR_EXAMPLE = os.path.join(MODULE_LOCATION, 'resources', 'crispr_example.xml')


class TestComponentDefinitions(unittest.TestCase):

    def setUp(self):
        pass

    def test_typesSet(self):
        # Constructs a protein component
        cas9 = sbol2.ComponentDefinition('Cas9', sbol2.BIOPAX_PROTEIN)
        self.assertEqual([sbol2.BIOPAX_PROTEIN], cas9.types)

    def test_typesNotSet(self):
        target_promoter = sbol2.ComponentDefinition('target_promoter')
        self.assertEqual([sbol2.BIOPAX_DNA], target_promoter.types)

    def testAddComponentDefinition(self):
        sbol2.setHomespace('http://sbols.org/CRISPR_Example')
        sbol2.Config.setOption('sbol_compliant_uris', True)
        sbol2.Config.setOption('sbol_typed_uris', False)
        expected = 'BB0001'
        test_CD = sbol2.ComponentDefinition(expected)
        doc = sbol2.Document()
        doc.addComponentDefinition(test_CD)
        self.assertIsNotNone(doc.componentDefinitions.get(expected))
        displayId = doc.componentDefinitions.get(expected).displayId
        self.assertEqual(str(displayId), expected)
        self.assertEqual(displayId, rdflib.Literal(expected))

    def testRemoveComponentDefinition(self):
        test_CD = sbol2.ComponentDefinition("BB0001")
        doc = sbol2.Document()
        doc.addComponentDefinition(test_CD)
        doc.componentDefinitions.remove(0)
        # NOTE: changed the test to expect the 'sbol error type'
        # as opposed to a RuntimeError.
        with self.assertRaises(sbol2.SBOLError):
            doc.componentDefinitions.get("BB0001")

    def testCDDisplayId(self):
        list_cd_read = []
        doc = sbol2.Document()
        doc.read(CRISPR_EXAMPLE)

        # List of displayIds
        list_cd = ['CRP_b', 'CRa_U6', 'EYFP', 'EYFP_cds', 'EYFP_gene',
                   'Gal4VP16', 'Gal4VP16_cds', 'Gal4VP16_gene',
                   'cas9_gRNA_complex', 'cas9_generic',
                   'cas9m_BFP', 'cas9m_BFP_cds',
                   'cas9m_BFP_gRNA_b', 'cas9m_BFP_gene',
                   'gRNA_b', 'gRNA_b_gene', 'gRNA_b_nc', 'gRNA_b_terminator',
                   'gRNA_generic', 'mKate', 'mKate_cds', 'mKate_gene',
                   'pConst', 'target', 'target_gene']

        for CD in doc.componentDefinitions:
            list_cd_read.append(CD.displayId)
        # Sort the list. Does doc.componentDefintions make any
        # guarantees about order?
        list_cd_read.sort()
        # Convert expected display ids to rdflib.Literals and compare
        self.assertSequenceEqual(list_cd_read,
                                 [rdflib.Literal(x) for x in list_cd])
        # Convert CD display ids to strings and compare
        self.assertSequenceEqual([str(x) for x in list_cd_read],
                                 list_cd)
        # Python 3 compatability
        if sys.version_info[0] < 3:
            self.assertItemsEqual(list_cd_read, list_cd)
        else:
            expected = [rdflib.Literal(x) for x in list_cd]
            self.assertCountEqual(list_cd_read, expected)

    # See Issue #64, CD.assemblePrimaryStructure is not implemented
    @unittest.expectedFailure  # See issue 64
    def testPrimaryStructureIteration(self):
        list_cd = []
        list_cd_true = ["R0010", "E0040", "B0032", "B0012"]
        doc = Document()
        gene = ComponentDefinition("BB0001")
        promoter = ComponentDefinition("R0010")
        rbs = ComponentDefinition("B0032")
        cds = ComponentDefinition("E0040")
        terminator = ComponentDefinition("B0012")

        doc.addComponentDefinition([gene, promoter, rbs, cds, terminator])

        gene.assemblePrimaryStructure([promoter, rbs, cds, terminator])
        primary_sequence = gene.getPrimaryStructure()
        for component in primary_sequence:
            list_cd.append(component.displayId)

        # Python 3 compatability
        if sys.version_info[0] < 3:
            self.assertItemsEqual(list_cd, list_cd_true)
        else:
            self.assertCountEqual(list_cd, list_cd_true)

    @unittest.expectedFailure
    def testInsertDownstream(self):
        doc = Document()
        gene = ComponentDefinition("BB0001")
        promoter = ComponentDefinition("R0010")
        rbs = ComponentDefinition("B0032")
        cds = ComponentDefinition("E0040")
        terminator = ComponentDefinition("B0012")

        doc.addComponentDefinition([gene, promoter, rbs, cds, terminator])
        gene.assemblePrimaryStructure([promoter, rbs, cds])
        primary_structure_components = gene.getPrimaryStructureComponents()
        c_promoter = primary_structure_components[0]
        c_rbs = primary_structure_components[1]
        c_cds = primary_structure_components[2]
        gene.insertDownstreamComponent(c_cds, terminator)
        primary_structure = gene.getPrimaryStructure()
        primary_structure = [cd.identity for cd in primary_structure]
        valid_primary_structure = [promoter.identity, rbs.identity,
                                   cds.identity, terminator.identity]
        self.assertListEqual(primary_structure, valid_primary_structure)

    @unittest.expectedFailure
    def testInsertUpstream(self):
        doc = sbol2.Document()
        gene = sbol2.ComponentDefinition("BB0001")
        promoter = sbol2.ComponentDefinition("R0010")
        rbs = sbol2.ComponentDefinition("B0032")
        cds = sbol2.ComponentDefinition("E0040")
        terminator = sbol2.ComponentDefinition("B0012")

        doc.addComponentDefinition([gene, promoter, rbs, cds, terminator])
        gene.assemblePrimaryStructure([rbs, cds, terminator])
        primary_structure_components = gene.getPrimaryStructureComponents()
        c_rbs = primary_structure_components[0]
        c_cds = primary_structure_components[1]
        c_terminator = primary_structure_components[2]
        gene.insertUpstreamComponent(c_rbs, promoter)
        primary_structure = gene.getPrimaryStructure()
        primary_structure = [cd.identity for cd in primary_structure]
        valid_primary_structure = [promoter.identity, rbs.identity,
                                   cds.identity, terminator.identity]
        self.assertListEqual(primary_structure, valid_primary_structure)

    @unittest.expectedFailure
    def testHasUpstreamComponent(self):
        uri = 'http://sbols.org/CRISPR_Example/gRNA_b_gene/1.0.0'
        doc = sbol2.Document()
        doc.read(CRISPR_EXAMPLE)
        cd = doc.componentDefinitions.get(uri)
        self.assertIsNotNone(cd)
        comps = {
            'http://sbols.org/CRISPR_Example/gRNA_b_gene/CRa_U6/1.0.0': True,
            'http://sbols.org/CRISPR_Example/gRNA_b_gene/CRa_U6/1.0.0': True,
            'http://sbols.org/CRISPR_Example/gRNA_b_gene/CRa_U6/1.0.0': False
        }
        uri = 'http://sbols.org/CRISPR_Example/gRNA_b_gene/CRa_U6/1.0.0'
        c = cd.components.get(uri)
        self.assertTrue(cd.hasUpstreamComponent(c))

    def testOwnedLocation(self):
        cd = sbol2.ComponentDefinition('cd')
        sa = cd.sequenceAnnotations.create('sa')
        r = sa.locations.createRange('r')
        self.assertEqual(type(r), sbol2.Range)
        r = sa.locations['r']
        self.assertEqual(type(r), sbol2.Range)
        gl = sa.locations.createGenericLocation('gl')
        self.assertEqual(type(gl), sbol2.GenericLocation)
        gl = sa.locations['gl']
        self.assertEqual(type(gl), sbol2.GenericLocation)
        self.assertEqual(len(sa.locations), 2)

    def testCut(self):
        cd = sbol2.ComponentDefinition('cd')
        sa = cd.sequenceAnnotations.create('sa')
        c = sa.locations.createCut('c')
        self.assertEqual(type(c), sbol2.Cut)
        c = sa.locations['c']
        self.assertEqual(type(c), sbol2.Cut)

    def test_get_range(self):
        cd = sbol2.ComponentDefinition('cd')
        sa = cd.sequenceAnnotations.create('sa')
        r = sa.locations.createRange('r')
        self.assertEqual(type(r), sbol2.Range)
        # SYNBICT uses getRange with no argument. It returns the first
        # object.
        r2 = sa.locations.getRange()
        self.assertEqual(r2, r)
        # getCut with zero args should raise a type error because the
        # first object is a Range.
        with self.assertRaises(TypeError):
            sa.locations.getCut()

    def test_get_cut(self):
        cd = sbol2.ComponentDefinition('cd')
        sa = cd.sequenceAnnotations.create('sa')
        c = sa.locations.createCut('c')
        self.assertEqual(type(c), sbol2.Cut)
        # SYNBICT uses getCut with no argument. It returns the first
        # object.
        c2 = sa.locations.getCut()
        self.assertEqual(c2, c)
        # getRange with zero args should raise a type error because
        # the first object is a Cut.
        with self.assertRaises(TypeError):
            sa.locations.getRange()


class TestAssemblyRoutines(unittest.TestCase):

    @unittest.expectedFailure
    def testAssemble(self):
        doc = sbol2.Document()
        gene = sbol2.ComponentDefinition("BB0001")
        promoter = sbol2.ComponentDefinition("R0010")
        RBS = sbol2.ComponentDefinition("B0032")
        CDS = sbol2.ComponentDefinition("E0040")
        terminator = sbol2.ComponentDefinition("B0012")

        promoter.sequence = sbol2.Sequence('R0010')
        RBS.sequence = sbol2.Sequence('B0032')
        CDS.sequence = sbol2.Sequence('E0040')
        terminator.sequence = sbol2.Sequence('B0012')

        promoter.sequence.elements = 'a'
        RBS.sequence.elements = 't'
        CDS.sequence.elements = 'c'
        terminator.sequence.elements = 'g'

        promoter.roles = sbol2.SO_PROMOTER
        RBS.roles = sbol2.SO_RBS
        CDS.roles = sbol2.SO_CDS
        terminator.roles = sbol2.SO_TERMINATOR

        doc.addComponentDefinition([gene, promoter, RBS, CDS, terminator])
        gene.assemblePrimaryStructure(['R0010', 'B0032', 'E0040', 'B0012'])
        primary_structure = gene.getPrimaryStructure()
        primary_structure = [c.identity for c in primary_structure]

        self.assertEqual(primary_structure, [promoter.identity, RBS.identity,
                         CDS.identity, terminator.identity])

    @unittest.expectedFailure
    def testCompileSequence(self):
        doc = sbol2.Document()
        sbol2.Config.setOption('sbol_typed_uris', True)
        gene = sbol2.ComponentDefinition("BB0001")
        promoter = sbol2.ComponentDefinition("R0010")
        CDS = sbol2.ComponentDefinition("B0032")
        RBS = sbol2.ComponentDefinition("E0040")
        terminator = sbol2.ComponentDefinition("B0012")
        scar = sbol2.ComponentDefinition('scar')

        promoter.sequence = sbol2.Sequence('R0010')
        RBS.sequence = sbol2.Sequence('B0032')
        CDS.sequence = sbol2.Sequence('E0040')
        terminator.sequence = sbol2.Sequence('B0012')
        scar.sequence = sbol2.Sequence('scar')

        promoter.sequence.elements = 'aaa'
        RBS.sequence.elements = 'aaa'
        CDS.sequence.elements = 'aaa'
        terminator.sequence.elements = 'aaa'
        scar.sequence.elements = 'ttt'

        doc.addComponentDefinition(gene)
        gene.assemblePrimaryStructure([promoter, scar, RBS, scar, CDS, scar,
                                      terminator])
        target_seq = gene.compile()

        self.assertEqual(target_seq, 'aaatttaaatttaaatttaaa')
        self.assertEqual(target_seq, gene.sequence.elements)

    @unittest.expectedFailure
    def testRecursiveCompile(self):
        doc = sbol2.Document()
        cd1 = sbol2.ComponentDefinition('cd1')
        cd2 = sbol2.ComponentDefinition('cd2')
        cd3 = sbol2.ComponentDefinition('cd3')
        cd4 = sbol2.ComponentDefinition('cd4')
        cd5 = sbol2.ComponentDefinition('cd5')
        cd1.sequence = sbol2.Sequence('cd1')
        cd2.sequence = sbol2.Sequence('cd2')
        cd3.sequence = sbol2.Sequence('cd3')
        cd4.sequence = sbol2.Sequence('cd4')
        cd5.sequence = sbol2.Sequence('cd5')
        cd1.sequence.elements = 'tt'
        cd2.sequence.elements = 'gg'
        cd3.sequence.elements = 'n'
        cd4.sequence.elements = 'aa'
        cd5.sequence.elements = 'n'
        doc.addComponentDefinition([cd1, cd2, cd3, cd4, cd5])
        cd3.assemblePrimaryStructure([cd1, cd2])
        cd5.assemblePrimaryStructure([cd4, cd3])
        cd5.compile()
        self.assertEquals(cd3.sequence.elements, 'ttgg')
        self.assertEquals(cd5.sequence.elements, 'aattgg')
        r1 = cd3.sequenceAnnotations['cd1_annotation_0'].\
            locations['cd1_annotation_0_range']
        r2 = cd3.sequenceAnnotations['cd2_annotation_0'].\
            locations['cd2_annotation_0_range']
        r4 = cd5.sequenceAnnotations['cd4_annotation_0'].\
            locations['cd4_annotation_0_range']
        self.assertEquals(r1.start, 3)
        self.assertEquals(r1.end, 4)
        self.assertEquals(r2.start, 5)
        self.assertEquals(r2.end, 6)
        self.assertEquals(r4.start, 1)
        self.assertEquals(r4.end, 2)

    @unittest.expectedFailure
    def testStandardAssembly(self):
        doc = sbol2.Document()
        gene = sbol2.ComponentDefinition("BB0001")
        promoter = sbol2.ComponentDefinition("R0010")
        RBS = sbol2.ComponentDefinition("B0032")
        CDS = sbol2.ComponentDefinition("E0040")
        terminator = sbol2.ComponentDefinition("B0012")

        promoter.sequence = sbol2.Sequence('R0010')
        RBS.sequence = sbol2.Sequence('B0032')
        CDS.sequence = sbol2.Sequence('E0040')
        terminator.sequence = sbol2.Sequence('B0012')

        promoter.sequence.elements = 'a'
        RBS.sequence.elements = 't'
        CDS.sequence.elements = 'c'
        terminator.sequence.elements = 'g'

        promoter.roles = sbol2.SO_PROMOTER
        RBS.roles = sbol2.SO_RBS
        CDS.roles = sbol2.SO_CDS
        terminator.roles = sbol2.SO_TERMINATOR

        doc.addComponentDefinition(gene)
        gene.assemblePrimaryStructure([promoter, RBS, CDS, terminator],
                                      IGEM_STANDARD_ASSEMBLY)
        target_seq = gene.compile()

        self.assertEquals(target_seq, 'atactagagttactagctactagagg')

    @unittest.expectedFailure
    def testAssembleWithDisplayIds(self):
        sbol2.Config.setOption('sbol_typed_uris', True)

        doc = sbol2.Document()
        gene = sbol2.ComponentDefinition("BB0001")
        promoter = sbol2.ComponentDefinition("R0010")
        RBS = sbol2.ComponentDefinition("B0032")
        CDS = sbol2.ComponentDefinition("E0040")
        terminator = sbol2.ComponentDefinition("B0012")

        promoter.sequence = sbol2.Sequence('R0010')
        RBS.sequence = sbol2.Sequence('B0032')
        CDS.sequence = sbol2.Sequence('E0040')
        terminator.sequence = sbol2.Sequence('B0012')

        promoter.sequence.elements = 'a'
        RBS.sequence.elements = 't'
        CDS.sequence.elements = 'c'
        terminator.sequence.elements = 'g'

        promoter.roles = sbol2.SO_PROMOTER
        RBS.roles = sbol2.SO_RBS
        CDS.roles = sbol2.SO_CDS
        terminator.roles = sbol2.SO_TERMINATOR

        doc.addComponentDefinition([gene, promoter, RBS, CDS, terminator])
        gene.assemblePrimaryStructure(['R0010', 'B0032', 'E0040', 'B0012'])
        primary_structure = gene.getPrimaryStructure()
        primary_structure = [c.identity for c in primary_structure]
        self.assertEqual(primary_structure, [promoter.identity, RBS.identity,
                         CDS.identity, terminator.identity])

        target_seq = gene.compile()
        self.assertEqual(target_seq, 'atcg')

    @unittest.expectedFailure
    def testDeleteUpstream(self):
        doc = sbol2.Document()
        gene = sbol2.ComponentDefinition("BB0001")
        promoter = sbol2.ComponentDefinition("R0010")
        rbs = sbol2.ComponentDefinition("B0032")
        cds = sbol2.ComponentDefinition("E0040")
        terminator = sbol2.ComponentDefinition("B0012")

        doc.addComponentDefinition([gene, promoter, rbs, cds, terminator])
        gene.assemblePrimaryStructure([promoter, rbs, cds, terminator])
        primary_structure_components = gene.getPrimaryStructureComponents()
        c_promoter = primary_structure_components[0]
        c_rbs = primary_structure_components[1]
        c_cds = primary_structure_components[2]
        c_terminator = primary_structure_components[3]

        gene.deleteUpstreamComponent(c_cds)
        primary_structure = gene.getPrimaryStructure()
        primary_structure = [cd.identity for cd in primary_structure]
        valid_primary_structure = [promoter.identity, cds.identity, terminator.identity]
        self.assertEqual(primary_structure, valid_primary_structure)

        # Test deletion when the target Component is the first Component
        gene.deleteUpstreamComponent(c_cds)
        primary_structure = gene.getPrimaryStructure()
        primary_structure = [cd.identity for cd in primary_structure]
        valid_primary_structure = [cds.identity, terminator.identity]
        self.assertEqual(primary_structure, valid_primary_structure)

        # Test failure when user tries to delete a Component upstream of the first
        # Component
        with self.assertRaises(ValueError):
            gene.deleteUpstreamComponent(c_promoter)
        # Test failure when the user supplies a Component that isn't part of the
        # primary structure
        with self.assertRaises(ValueError):
            gene.deleteUpstreamComponent(Component())

    @unittest.expectedFailure
    def testDeleteDownstream(self):
        doc = sbol2.Document()
        gene = sbol2.ComponentDefinition("BB0001")
        promoter = sbol2.ComponentDefinition("R0010")
        rbs = sbol2.ComponentDefinition("B0032")
        cds = sbol2.ComponentDefinition("E0040")
        terminator = sbol2.ComponentDefinition("B0012")

        doc.addComponentDefinition([gene, promoter, rbs, cds, terminator])
        gene.assemblePrimaryStructure([promoter, rbs, cds, terminator])
        primary_structure_components = gene.getPrimaryStructureComponents()
        c_promoter = primary_structure_components[0]
        c_rbs = primary_structure_components[1]
        c_cds = primary_structure_components[2]
        c_terminator = primary_structure_components[3]

        gene.deleteDownstreamComponent(c_rbs)
        primary_structure = gene.getPrimaryStructure()
        primary_structure = [cd.identity for cd in primary_structure]
        valid_primary_structure = [promoter.identity, rbs.identity, terminator.identity]
        self.assertEqual(primary_structure, valid_primary_structure)

        # Test deletion when the target Component is the last Component
        gene.deleteDownstreamComponent(c_rbs)
        primary_structure = gene.getPrimaryStructure()
        primary_structure = [cd.identity for cd in primary_structure]
        valid_primary_structure = [promoter.identity, rbs.identity]
        self.assertEqual(primary_structure, valid_primary_structure)

        # Test failure when user tries to delete Component upstream of the first
        # Component
        with self.assertRaises(ValueError):
            gene.deleteDownstreamComponent(c_cds)
        # Test failure when the user supplies a Component that isn't part of the
        # primary structure
        with self.assertRaises(ValueError):
            gene.deleteDownstreamComponent(Component())

    @unittest.expectedFailure
    def testInsertDownstream(self):
        doc = sbol2.Document()
        gene = sbol2.ComponentDefinition("BB0001")
        promoter = sbol2.ComponentDefinition("R0010")
        rbs = sbol2.ComponentDefinition("B0032")
        cds = sbol2.ComponentDefinition("E0040")
        terminator = sbol2.ComponentDefinition("B0012")

        doc.addComponentDefinition([gene, promoter, rbs, cds, terminator])
        gene.assemblePrimaryStructure([promoter, rbs, cds])
        primary_structure_components = gene.getPrimaryStructureComponents()
        c_promoter = primary_structure_components[0]
        c_rbs = primary_structure_components[1]
        c_cds = primary_structure_components[2]
        gene.insertDownstreamComponent(c_cds, terminator)
        primary_structure = gene.getPrimaryStructure()
        primary_structure = [cd.identity for cd in primary_structure]
        valid_primary_structure = [promoter.identity, rbs.identity, cds.identity,
                                   terminator.identity]
        self.assertEqual(primary_structure, valid_primary_structure)

    @unittest.expectedFailure
    def testInsertUpstream(self):
        doc = sbol2.Document()
        gene = sbol2.ComponentDefinition("BB0001")
        promoter = sbol2.ComponentDefinition("R0010")
        rbs = sbol2.ComponentDefinition("B0032")
        cds = sbol2.ComponentDefinition("E0040")
        terminator = sbol2.ComponentDefinition("B0012")

        doc.addComponentDefinition([gene, promoter, rbs, cds, terminator])
        gene.assemblePrimaryStructure([rbs, cds, terminator])
        primary_structure_components = gene.getPrimaryStructureComponents()
        c_rbs = primary_structure_components[0]
        c_cds = primary_structure_components[1]
        c_terminator = primary_structure_components[2]
        gene.insertUpstreamComponent(c_rbs, promoter)
        primary_structure = gene.getPrimaryStructure()
        primary_structure = [cd.identity for cd in primary_structure]
        valid_primary_structure = [promoter.identity, rbs.identity, cds.identity,
                                   terminator.identity]
        self.assertEqual(primary_structure, valid_primary_structure)
