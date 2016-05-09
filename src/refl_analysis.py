import FWCore.ParameterSet.Config as cms

process = cms.Process("ReflectionAnalysis")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(10000) )

#
#   Command Line Input(Copied from DQM for now)
#
import sys
if len(sys.argv)!= 3:
    print "### ERROR: No Run File has been provided"
    print "### Use: cmsRun h2testbeamanalyzer_cfg.py <run number>"
    sys.exit(1)

#
#   Change the filename to process
#
runNumber = sys.argv[2]

process.source = cms.Source("HcalTBSource",
    fileNames = cms.untracked.vstring(
        'file:/afs/cern.ch/work/j/jmariano/public/904_runs/B904_Integration_'+runNumber+'.root'
    )
)

process.options = cms.untracked.PSet(
        wantSummary = cms.untracked.bool(False)
        )

process.tbunpack = cms.EDProducer("HcalTBObjectUnpacker",
        IncludeUnmatchedHits = cms.untracked.bool(False),
        ConfigurationFile=cms.untracked.string('HFcommissioning/Analysis/test/configQADCTDC.txt'),
        HcalSlowDataFED = cms.untracked.int32(3),
        HcalTriggerFED = cms.untracked.int32(1),
        HcalTDCFED = cms.untracked.int32(8),
        HcalQADCFED = cms.untracked.int32(8),
        fedRawDataCollectionTag = cms.InputTag('source')
)

process.hcalDigis = cms.EDProducer("HcalRawToDigi",
                                   #       UnpackHF = cms.untracked.bool(True),
                                   ### Falg to enable unpacking of TTP channels(default = false)
                                   ### UnpackTTP = cms.untracked.bool(True),
                                   FilterDataQuality = cms.bool(False),
                                   InputLabel = cms.InputTag('source'),
                                   HcalFirstFED = cms.untracked.int32(928),
                                   ComplainEmptyData = cms.untracked.bool(False),
                                   #       UnpackCalib = cms.untracked.bool(True),
                                   FEDs = cms.untracked.vint32(928,930),
                                   firstSample = cms.int32(0),
                                   lastSample = cms.int32(10)
                                   )


process.hcalAnalyzer = cms.EDAnalyzer('HF_refl_analyzer',
        OutFileName = cms.untracked.string('../data/Analysis_'+runNumber+'.root'),
        Verbosity = cms.untracked.int32(0)
)

#
#   For Debugging: Create a Pool Output Module
#
#process.output = cms.OutputModule(
#        'PoolOutputModule',
#        fileName = cms.untracked.string('HFanalysis_'+runNumber+'.root')
#)

process.load('Configuration.Geometry.GeometryIdeal_cff')

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.autoCond import autoCond
from CondCore.DBCommon.CondDBSetup_cfi import *

process.GlobalTag.globaltag = autoCond['startup'] 

#   EMAP Needed for H2 DATA
process.es_ascii = cms.ESSource('HcalTextCalibrations',
        input = cms.VPSet(
               cms.PSet(
                object = cms.string('ElectronicsMap'),
                file = cms.FileInPath('HFcommissioning/QIE10_testing/cfg/EMAP-2CH.txt')
                )
        )
)

process.es_prefer = cms.ESPrefer('HcalTextCalibrations', 'es_ascii')

process.dump = cms.EDAnalyzer("HcalDigiDump")

process.p = cms.Path(process.hcalDigis
#                     *process.dump
                     *process.hcalAnalyzer
                     )
#process.outpath = cms.EndPath(process.output)

