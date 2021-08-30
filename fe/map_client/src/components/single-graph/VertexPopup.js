import React, {Component} from 'react';
import {Popup} from "react-leaflet";
import {array, func, string} from "prop-types";
import SearchBar from "../searchBar/SearchBar";
import Autocompletion from "../autocompletion/Autocompletion";
import './leafletPopup.scss'
import {postVertexMetadata} from "../../APILayer";

class VertexPopup extends Component {
    constructor(props) {
        super(props);
        this.state = {
            recentlyAddedMetadata: [],
            currentInput: '',
            showAutocompletion: false
        }
        this.vertexAddMetadataCallback = this.vertexAddMetadataCallback.bind(this)
        this.onBlur = this.onBlur.bind(this);
    }

    render() {
        let addedMetadata = this.getAddedMetadata();
        return (
            <Popup>
                <>
                    <div><span>Types : </span> <span>{this.props.typesConcatenated + addedMetadata['type']}</span></div>
                    <div><span>Labels : </span> <span>{this.props.labelsConcatenated + addedMetadata['label']}</span>
                    </div>
                    <a href={'https://etherscan.io/address/' + this.props.eth}
                       target="_blank">{this.props.eth}</a>

                    <SearchBar
                        onChange={(v) => this.setState({
                            currentInput: v
                        })}
                        onBlur={this.onBlur}
                        onFocus={() => {
                            this.setState({showAutocompletion: true})
                        }}/>
                    <Autocompletion currentInput={this.state.currentInput}
                                    shouldRender={this.state.showAutocompletion}
                                    recentMetadataSearches={[]}
                                    onClick={(metadataObject) => {
                                        postVertexMetadata(this.props.eth, metadataObject)
                                        this.setState({recentlyAddedMetadata: [...this.state.recentlyAddedMetadata, metadataObject]})
                                    }}/>
                    {/*<searchBar*/}
                    {/*    showSelected={false}*/}
                    {/*    graphName={this.props.graphName}*/}
                    {/*    graphId={this.props.graphId}*/}
                    {/*    selectedMetadataCallback={this.vertexAddMetadataCallback}*/}
                    {/*    recentMetadataSearches={this.props.recentMetadataSearches}*/}
                    {/*    placeholder={'ADD METADATA'}/>*/}
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

    vertexAddMetadataCallback(currentSelection) {
        this.props.selectionCallback(currentSelection[currentSelection.length - 1])
        this.setState({
            recentlyAddedMetadata: [...currentSelection]
        })
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
    eth: string.isRequired,
    selectionCallback: func.isRequired,
    typesConcatenated: string.isRequired,
    labelsConcatenated: string.isRequired,
    graphName: string.isRequired,
    recentMetadataSearches: array.isRequired
}

VertexPopup.defaultProps = {
    typesConcatenated: "",
    labelsConcatenated: "",
}

export default VertexPopup;