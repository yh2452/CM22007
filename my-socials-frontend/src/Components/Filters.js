//import { useState } from "react";

const Filters = ({filterData, changeData}) => {



    return (
        <div className="container">
        <h1 className="title">MySocials</h1>
        <form>  {/* Search Form */}
            <input
            type="search"
            name="search"
            value={filterData.search}
            onChange={(e) => changeData.changeSearch(e.target.value)}
            placeholder="Search..."
            className="input"
            />
        </form>
        
        <div>  {/* Sort direction */}
            <select
            id="sortDropdown"
            name="sort"
            value={filterData.sort}
            onChange={(e) => changeData.changeSort(e.target.value)}
            className="dropdown"
            >
            <option value="option1">Soonest upcoming</option>
            <option value="option2">Newest added</option>
            </select>
        </div>

        <div> {/* Calendar */}
            <input type="date" value={filterData.startDate} onChange={(e) => changeData.changeStartDate(e.target.value)} className="input" />
            <span style={{ margin: "0 10px" }}> - </span>
            <input type="date" value={filterData.endDate} onChange={(e) => changeData.changeEndDate(e.target.value)} className="input" />
        </div>
        
        <div className="date-time-container">
            <input type="time" value={filterData.startTime} onChange={(e) => changeData.changeStartTime(e.target.value)} className="input" />
            <span style={{ margin: "0 10px" }}> - </span>
            <input type="time" value={filterData.endTime} onChange={(e) => changeData.changeEndTime(e.target.value)} className="input" />
        </div>

        <div>  {/* Filters */}
            {Object.keys(filterData.filters).map((filterKey) => (
            <div key={filterKey} className="checkbox-item">
                <input
                type="checkbox"
                id={filterKey}
                name={filterKey}
                checked={filterData.filters[filterKey]}
                onChange={changeData.changeFilters}
                />
                <label htmlFor={filterKey} className="checkbox-label">
                {filterKey.replace(/([A-Z])/g, ' $1')}
                </label>
            </div>
            ))}
        </div>
        </div>
    );
};

export default Filters;