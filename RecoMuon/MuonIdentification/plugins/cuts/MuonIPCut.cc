#include "PhysicsTools/SelectorUtils/interface/CutApplicatorBase.h"
#include "PhysicsTools/SelectorUtils/interface/CutApplicatorWithEventContentBase.h"
#include "DataFormats/MuonReco/interface/Muon.h"
#include "DataFormats/MuonReco/interface/MuonSelectors.h"

class MuonIPCut : public CutApplicatorWithEventContentBase
{
public:
  MuonIPCut(const edm::ParameterSet& c);

  result_type operator()(const reco::MuonPtr&) const override final;
  CandidateType candidateType() const override final { return MUON; }
  double value(const reco::CandidatePtr&) const override final;

  void setConsumes(edm::ConsumesCollector&) override final;
  void getEventContent(const edm::EventBase&) override final;

private:
  edm::Handle<reco::VertexCollection> vtxs_;
  const double maxDxy_, maxDz_;
  enum BestTrackType { INNERTRACK, MUONBESTTRACK, NONE } trackType_;
};
DEFINE_EDM_PLUGIN(CutApplicatorFactory,
                  MuonIPCut, "MuonIPCut");

// Define constructors and initialization routines
MuonIPCut::MuonIPCut(const edm::ParameterSet& c):
  CutApplicatorWithEventContentBase(c),
  maxDxy_(c.getParameter<double>("maxDxy")),
  maxDz_(c.getParameter<double>("maxDz"))
{
  const std::string trackTypeName = c.getParameter<std::string>("trackType");
  trackType_ = NONE;
  if      ( trackTypeName == "muonBestTrack" ) trackType_ = MUONBESTTRACK;
  else if ( trackTypeName == "innerTrack" ) trackType_ = INNERTRACK;
  else
  {
    edm::LogError("MuonIPCut") << "Wrong cut id name, " << trackTypeName
                                        << "Choose among \"muonBestTrack\", \"innerTrack\"";
    trackType_ = NONE;
  }

  contentTags_.emplace("vertices", c.getParameter<edm::InputTag>("vertexSrc"));
  contentTags_.emplace("verticesMiniAOD", c.getParameter<edm::InputTag>("vertexSrcMiniAOD"));
}

void MuonIPCut::setConsumes(edm::ConsumesCollector& cc)
{
  contentTokens_.emplace("vertices", cc.consumes<reco::VertexCollection>(contentTags_["vertices"]));
  contentTokens_.emplace("verticesMiniAOD", cc.consumes<reco::VertexCollection>(contentTags_["verticesMiniAOD"]));
}

void MuonIPCut::getEventContent(const edm::EventBase& ev)
{
  ev.getByLabel(contentTags_["vertices"], vtxs_);
  if ( !vtxs_.isValid() ) ev.getByLabel(contentTags_["verticesMiniAOD"], vtxs_);
}

// Functors for evaluation
CutApplicatorBase::result_type MuonIPCut::operator()(const reco::MuonPtr& cand) const
{
  const auto& vtxPos = vtxs_->at(0).position();

  reco::TrackRef trackRef;
  if      ( trackType_ == INNERTRACK    ) trackRef = cand->innerTrack();
  else if ( trackType_ == MUONBESTTRACK ) trackRef = cand->muonBestTrack();
  if ( trackRef.isNull() ) return false;

  const double dxy = std::abs(trackRef->dxy(vtxPos));
  if ( dxy > maxDxy_ ) return false;

  const double dz = std::abs(trackRef->dz(vtxPos));
  if ( dz > maxDz_ ) return false;

  return true;
}

double MuonIPCut::value(const reco::CandidatePtr& cand) const
{
  const reco::MuonPtr muon(cand);
  reco::TrackRef trackRef;
  if      ( trackType_ == INNERTRACK    ) trackRef = muon->innerTrack();
  else if ( trackType_ == MUONBESTTRACK ) trackRef = muon->muonBestTrack();
  if ( trackRef.isNull() ) return -1;

  const auto& vtxPos = vtxs_->at(0).position();
  double dxy = std::abs(trackRef->dxy(vtxPos));
  if ( dxy > maxDxy_ ) return dxy;

  const double dz = std::abs(trackRef->dz(vtxPos));
  if ( dz > maxDz_ ) return dz;

  return dz;
}
