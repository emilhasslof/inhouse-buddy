import React, { useState, useEffect } from 'react';
import jsonData from './data.json';

function LeagueStatsTable() {
  const [data, setData] = useState([]);

  useEffect(() => {
    setData(jsonData.sort((a, b) => b.points - a.points));
  }, []);

  return (
    <table>
      <thead>
        <tr>
          <th>Player Name</th>
          <th>Wins</th>
          <th>Losses</th>
          <th>Points</th>
        </tr>
      </thead>
      <tbody>
        {data.map((player) => (
          <tr key={player.name}>
            <td>{player.name}</td>
            <td>{player.wins}</td>
            <td>{player.losses}</td>
            <td>{player.points}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default LeagueStatsTable;
