import React, {Component} from 'react';
import {Popup} from "react-leaflet";
import {array, object, string} from "prop-types";
import SearchBar from "../searchBar/SearchBar";
import Autocompletion from "../autocompletion/Autocompletion";
import './leafletPopup.scss'
import {postVertexMetadata} from "../../APILayer";
import './testCustomControl.css'

class VertexPopup extends Component {

    constructor(props) {
        super(props);
        this.state = {
            recentlyAddedMetadata: [],
            currentInput: '',
            showAutocompletion: false,
        }
        this.onBlur = this.onBlur.bind(this);
    }

    render() {
        let addedMetadata = this.getAddedMetadata();
        let labelsString = this.props.vertexObject['labels'] === null ? 'NA' : this.props.vertexObject['labels'].join(', ');
        let typesString = this.props.vertexObject['types'] === null ? 'NA' : this.props.vertexObject['types'].join(', ');
        return (
            <Popup>
                <>
                    <div><span>Types : </span> <span>{typesString + addedMetadata['type']}</span></div>
                    <div><span>Labels : </span> <span>{labelsString + addedMetadata['label']}</span>
                    </div>
                    <a href={'https://etherscan.io/address/' + this.props.vertexObject['vertex']}
                       target="_blank">{this.props.vertexObject['vertex']}</a>

                    <SearchBar
                        onChange={(v) => this.setState({
                            currentInput: v
                        })}
                        onBlur={this.onBlur}
                        onFocus={() => {
                            this.setState({showAutocompletion: true})
                        }}/>
                    <Autocompletion
                        autocompletionTerms={this.props.autocompletionTerms}
                        currentInput={this.state.currentInput}
                        shouldRender={this.state.showAutocompletion}
                        recentMetadataSearches={[]}
                        onClick={(metadataObject) => {
                            postVertexMetadata(this.props.vertexObject['vertex'], metadataObject)
                            this.setState({recentlyAddedMetadata: [...this.state.recentlyAddedMetadata, metadataObject]})
                    }}/>
                    <div>
                        <form>
                            <div className={"map-checkbox-container"}>
                                <label>
                                    <input className={"map-checkbox-small"}
                                        id="persist-edges"
                                        type="checkbox"
                                        checked={this.props.ticked}
                                        onChange={this.props.checkboxCallback}>
                                    </input>
                                    <span>Persist</span>
                                </label>
                            </div>
                        </form>
                    </div>
                </>
            </Popup>
        );
    }

    getAddedMetadata() {
        let addition = {'type': ' ', 'label': ' '}
        if (this.state.recentlyAddedMetadata.length > 0) {
            for (const metadataObject of this.state.recentlyAddedMetadata) {
                addition[metadataObject['type']] += metadataObject['value'] + " ";
            }
        }
        return addition;
    }

    onBlur(e) {
        let wasAutocompleteTermClicked = e.relatedTarget !== null && e.relatedTarget.className.includes('dont-lose-focus');
        // console.log("blurring, wasAutocompleteTermClicked ", wasAutocompleteTermClicked)
        if (wasAutocompleteTermClicked) {
            return
        }
        // the user clicked somewhere else on the map
        this.setState({
            showAutocompletion: false
        })
    }
}

VertexPopup.propTypes = {
    vertexObject: object.isRequired,
    typesConcatenated: string.isRequired,
    labelsConcatenated: string.isRequired,
    graphName: string.isRequired
}

VertexPopup.defaultProps = {
    typesConcatenated: "",
    labelsConcatenated: "",
}

export default VertexPopup;