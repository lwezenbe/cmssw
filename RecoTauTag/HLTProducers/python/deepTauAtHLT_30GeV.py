import FWCore.ParameterSet.Config as cms

from RecoTauTag.RecoTau.PFRecoTauDiscriminationByIsolation_cfi import *
from RecoTauTag.RecoTau.PFRecoTauQualityCuts_cfi import PFTauQualityCuts
from RecoTauTag.RecoTau.PFRecoTauDiscriminationByHPSSelection_cfi import hpsSelectionDiscriminator

from RecoTauTag.RecoTau.PFTauPrimaryVertexProducer_cfi      import *
from RecoTauTag.RecoTau.PFTauSecondaryVertexProducer_cfi    import *
from RecoTauTag.RecoTau.PFTauTransverseImpactParameters_cfi import *

from RecoTauTag.RecoTau.DeepTau_cfi import *

from RecoTauTag.RecoTau.PFRecoTauPFJetInputs_cfi import PFRecoTauPFJetInputs
## DeltaBeta correction factor
ak4dBetaCorrection = 0.20

def update(process):
    process.options.wantSummary = cms.untracked.bool(True)

    process.hltFixedGridRhoFastjetAllTau = cms.EDProducer( "FixedGridRhoProducerFastjet",
        gridSpacing = cms.double( 0.55 ),
        maxRapidity = cms.double( 5.0 ),
        pfCandidatesTag = cms.InputTag( "hltParticleFlowReg" )
    )

    PFTauQualityCuts.primaryVertexSrc = cms.InputTag("hltPixelVertices")

    ## Decay mode prediscriminant
    requireDecayMode = cms.PSet(
        BooleanOperator = cms.string("and"),
        decayMode = cms.PSet(
            Producer = cms.InputTag('hltHpsPFTauDiscriminationByDecayModeFindingNewDMsReg'),
            cut = cms.double(0.5)
        )
    )

    ## Cut based isolations dR=0.5
    process.hpsPFTauBasicDiscriminatorsForDeepTau = pfRecoTauDiscriminationByIsolation.clone(
        PFTauProducer = 'hltHpsPFTauProducerReg',
        Prediscriminants = cms.PSet(  BooleanOperator = cms.string( "and" ) ),
        deltaBetaPUTrackPtCutOverride     = True, # Set the boolean = True to override.
        deltaBetaPUTrackPtCutOverride_val = 0.5,  # Set the value for new value.
        particleFlowSrc = 'hltParticleFlowReg',
        vertexSrc = PFTauQualityCuts.primaryVertexSrc,
        customOuterCone = PFRecoTauPFJetInputs.isolationConeSize,
        isoConeSizeForDeltaBeta = 0.8,
        deltaBetaFactor = "%0.4f"%(ak4dBetaCorrection),
        qualityCuts = dict(isolationQualityCuts = dict(minTrackHits = 3, minGammaEt = 1.0, minTrackPt = 0.5)),
        IDdefinitions = [
            cms.PSet(
                IDname = cms.string("ChargedIsoPtSum"),
                ApplyDiscriminationByTrackerIsolation = cms.bool(True),
                storeRawSumPt = cms.bool(True)
            ),
            cms.PSet(
                IDname = cms.string("NeutralIsoPtSum"),
                ApplyDiscriminationByECALIsolation = cms.bool(True),
                storeRawSumPt = cms.bool(True)
            ),
            cms.PSet(
                IDname = cms.string("NeutralIsoPtSumWeight"),
                ApplyDiscriminationByWeightedECALIsolation = cms.bool(True),
                storeRawSumPt = cms.bool(True),
                UseAllPFCandsForWeights = cms.bool(True)
            ),
            cms.PSet(
                IDname = cms.string("TauFootprintCorrection"),
                storeRawFootprintCorrection = cms.bool(True)
            ),
            cms.PSet(
                IDname = cms.string("PhotonPtSumOutsideSignalCone"),
                storeRawPhotonSumPt_outsideSignalCone = cms.bool(True)
            ),
            cms.PSet(
                IDname = cms.string("PUcorrPtSum"),
                applyDeltaBetaCorrection = cms.bool(True),
                storeRawPUsumPt = cms.bool(True)
            ),
        ],
    )

    ## Cut based isolations dR=0.3
    process.hpsPFTauBasicDiscriminatorsdR03ForDeepTau = process.hpsPFTauBasicDiscriminatorsForDeepTau.clone(
        customOuterCone = 0.3
    )

    process.hpsPFTauPrimaryVertexProducerForDeepTau = PFTauPrimaryVertexProducer.clone(
        PFTauTag = "hltHpsPFTauProducerReg",
        ElectronTag = "hltEgammaCandidates",
        MuonTag = "hltMuonsReg",
        PVTag = "hltPixelVertices",
        beamSpot = "hltOnlineBeamSpot",
        discriminators = [
            cms.PSet(
                discriminator = cms.InputTag('hltHpsPFTauDiscriminationByDecayModeFindingNewDMsReg'),
                selectionCut = cms.double(0.5)
            )
        ],
        cut = "pt > 18.0 & abs(eta) < 2.4",
        qualityCuts = PFTauQualityCuts
    )

    process.hpsPFTauSecondaryVertexProducerForDeepTau = PFTauSecondaryVertexProducer.clone(
        PFTauTag = "hltHpsPFTauProducerReg"
    )
    process.hpsPFTauTransverseImpactParametersForDeepTau = PFTauTransverseImpactParameters.clone(
        PFTauTag = "hltHpsPFTauProducerReg",
        PFTauPVATag = "hpsPFTauPrimaryVertexProducerForDeepTau",
        PFTauSVATag = "hpsPFTauSecondaryVertexProducerForDeepTau",
        useFullCalculation = True
    )

    chargedIsolationQualityCuts = PFTauQualityCuts.clone(
        isolationQualityCuts = cms.PSet( 
            maxDeltaZ = cms.double( 0.2 ),
            minTrackPt = cms.double( 0.5 ),
            minGammaEt = cms.double( 0.5 ),
            minTrackHits = cms.uint32( 3 ),
            minTrackPixelHits = cms.uint32( 0 ),
            maxTrackChi2 = cms.double( 100.0 ),
            maxTransverseImpactParameter = cms.double( 0.1 ),
            useTracksInsteadOfPFHadrons = cms.bool( False )
        ),
        primaryVertexSrc = cms.InputTag( "hltPixelVertices" ),
        signalQualityCuts = cms.PSet( 
            maxDeltaZ = cms.double( 0.2 ),
            minTrackPt = cms.double( 0.0 ),
            minGammaEt = cms.double( 0.5 ),
            minTrackHits = cms.uint32( 3 ),
            minTrackPixelHits = cms.uint32( 0 ),
            maxTrackChi2 = cms.double( 1000.0 ),
            maxTransverseImpactParameter = cms.double( 0.2 ),
            useTracksInsteadOfPFHadrons = cms.bool( False ),
            minNeutralHadronEt = cms.double( 1.0 )
        ),
        vxAssocQualityCuts = cms.PSet( 
            minTrackPt = cms.double( 0.0 ),
            minGammaEt = cms.double( 0.5 ),
            minTrackHits = cms.uint32( 3 ),
            minTrackPixelHits = cms.uint32( 0 ),
            maxTrackChi2 = cms.double( 1000.0 ),
            maxTransverseImpactParameter = cms.double( 0.2 ),
            useTracksInsteadOfPFHadrons = cms.bool( False )
        ),
    )

    process.hltHpsL1JetsHLTDoublePFTauTrackPt1MediumChargedIsolationMatchReg.JetSrc = 'hltHpsPFTauProducerReg'
    process.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg_v4.remove(process.hltHpsL1JetsHLTDoublePFTauTrackPt1MediumChargedIsolationMatchReg)

    file_names = [
    				'core:RecoTauTag/TrainingFiles/data/DeepTauId/deepTau_2017v2p6_e6_core.pb',
    				'inner:RecoTauTag/TrainingFiles/data/DeepTauId/deepTau_2017v2p6_e6_inner.pb',
    				'outer:RecoTauTag/TrainingFiles/data/DeepTauId/deepTau_2017v2p6_e6_outer.pb',
    			]

    def getLinExpression(x1, x2, y1, y2):
        return "(((({3}-{2})/({1}-{0}))*(pt-{0}))+{2})".format(x1, x2, y1, y2)

    val1, val2 = ("0.57251451", "0.125")
    working_points = ["{0}*(pt < 30)+".format(val1)+getLinExpression("30", "300", val1, val2)+ "*(30 <= pt && pt < 300) + {0}*(pt >= 300)".format(val2)]

    process.deepTauProducer = DeepTau.clone(
        taus = 'hltHpsPFTauProducerReg',
        taus_to_compare = 'hltHpsL1JetsHLTDoublePFTauTrackPt1MediumChargedIsolationMatchReg',
        pfcands = 'hltParticleFlowReg',
        vertices = 'hltPixelVertices',
        rho = 'hltFixedGridRhoFastjetAllTau',
        graph_file = file_names,
        disable_dxy_pca = cms.bool(True),
        is_online = cms.bool(True),
        basicTauDiscriminators = 'hpsPFTauBasicDiscriminatorsForDeepTau',
        basicTauDiscriminatorsdR03 = 'hpsPFTauBasicDiscriminatorsdR03ForDeepTau',
        pfTauTransverseImpactParameters = 'hpsPFTauTransverseImpactParametersForDeepTau',
        Prediscriminants = cms.PSet(  BooleanOperator = cms.string( "and" ) ),  
        workingPoints = cms.vstring(['test']),
        rawValues = cms.vstring(['test']),
        VSeWP = working_points,
        VSmuWP = working_points,
        VSjetWP = working_points     
    )	

    # Add DeepTauProducer
    process.HLTHPSDeepTau30IsoPFTauSequenceReg = cms.Sequence(process.hpsPFTauPrimaryVertexProducerForDeepTau + process.hpsPFTauSecondaryVertexProducerForDeepTau + process.hpsPFTauTransverseImpactParametersForDeepTau + process.hltFixedGridRhoFastjetAllTau + process.hpsPFTauBasicDiscriminatorsForDeepTau + process.hpsPFTauBasicDiscriminatorsdR03ForDeepTau + process.hltHpsL1JetsHLTDoublePFTauTrackPt1MediumChargedIsolationMatchReg + process.deepTauProducer)
    process.hltHpsSelectedPFTausTrackPt1DeepTau30IsolationReg = process.hltHpsSelectedPFTausTrackPt1MediumChargedIsolationReg.clone(
        discriminators = [
            cms.PSet(  
                discriminator = cms.InputTag( "hltHpsPFTauTrackPt1DiscriminatorReg" ),
                selectionCut = cms.double( 0.5 )
            )
        ],
        discriminatorContainers = [
            cms.PSet(  discriminator = cms.InputTag( "deepTauProducer", "VSjet" ),
                rawValues = cms.vstring(),
                selectionCuts = cms.vdouble(),
                workingPoints = cms.vstring(['test']),
            )
        ]
    )

    process.hltHpsDoublePFTau30TrackPt1DeepTau30IsolationReg = process.hltHpsDoublePFTau30TrackPt1MediumChargedIsolationReg.clone(
        inputTag = "hltHpsSelectedPFTausTrackPt1DeepTau30IsolationReg",
    )

    process.hltHpsDoublePFTau30TrackPt1DeepTau30IsolationDz02Reg = process.hltHpsDoublePFTau30TrackPt1MediumChargedIsolationDz02Reg.clone(
        JetSrc = "hltHpsSelectedPFTausTrackPt1DeepTau30IsolationReg",
    )

    process.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg_v4.remove(process.HLTHPSDoublePFTauPt35Eta2p1Trk1Reg)
    process.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg_v4.remove(process.HLTHPSMediumChargedIsoPFTauSequenceReg)
    process.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg_v4.remove(process.hltHpsSelectedPFTausTrackPt1MediumChargedIsolationReg)
    process.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg_v4.remove(process.hltHpsDoublePFTau35TrackPt1MediumChargedIsolationReg)
    process.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg_v4.remove(process.hltHpsDoublePFTau35TrackPt1MediumChargedIsolationL1HLTMatchedReg)
    process.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg_v4.remove(process.hltHpsDoublePFTau35TrackPt1MediumChargedIsolationDz02Reg)
    
    process.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg_v4 += (process.HLTHPSDoublePFTauPt30Eta2p1Trk1Reg + process.HLTHPSDeepTau30IsoPFTauSequenceReg + process.hltHpsSelectedPFTausTrackPt1DeepTau30IsolationReg + process.hltHpsDoublePFTau30TrackPt1DeepTau30IsolationReg + process.hltHpsDoublePFTau30TrackPt1DeepTau30IsolationDz02Reg)

    return process

