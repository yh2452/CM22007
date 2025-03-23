import Filters from './Components/Filters'
import Event from './Components/Event';
import { useState  } from 'react';

function App() {
  const [events, setEvents] = useState ([])
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("option1");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [filters, setFilters] = useState({
  Subscribed: false,
  Favourited: false,
  OnCampus: false,
  SocietyEvent: false,
  TicketedEvent: false,
  });

  const changeSearch = (newData) => {
    setSearch(newData);
  };
  
  const changeSort = (newData) => {
    setSort(newData);
  };
  
  const changeStartDate = (newData) => {
    setStartDate(newData);
  };
  
  const changeEndDate = (newData) => {
    setEndDate(newData);
  };
  
  const changeStartTime = (newData) => {
    setStartTime(newData);
  };
  
  const changeEndTime = (newData) => {
    setEndTime(newData);
  };
  
  const changeFilters = (e) => {
    const { name, checked } = e.target;
    setFilters((prevFilters) => ({
        ...prevFilters,
        [name]: checked,
    }));
    console.log(filters);
};
  
  


  const filterData = {
    search,
    sort,
    startDate,
    endDate,
    startTime,
    endTime,
    filters,
  };

  const changeData = {
    changeSearch,
    changeSort,
    changeStartDate,
    changeEndDate,
    changeStartTime,
    changeEndTime,
    changeFilters,
  };

  return (
    <div>
      <div>
        <Filters 
        filterData = {filterData}
        changeData = {changeData}
        />
        <div>
          {/* Society list */}
        </div>
      </div>
      <div>
        {/* Event List */}
        {events.map((event) => ( //every item(post) in the posts array is passed through a UserPost component.
            <Event key = {event.id} event = {event} /> 
          ))}
      </div>
    </div>
  );
}

export default App;