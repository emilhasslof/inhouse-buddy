import React, { useState, useEffect } from 'react';
import jsonData from './data.json';
import './LeagueStatsTable.css';

function LeagueStatsTable() {
    const [tableData, setTableData] = useState([]);
    const [sortField, setSortField] = useState('points');
    const [sortOrder, setSortOrder] = useState('desc');

    useEffect(() => {
        const data = Object.entries(jsonData).map(([key, value]) => ({ name: key, ...value }));
        const sortedData = data.sort((a, b) => {
            if (a[sortField] > b[sortField]) {
                return sortOrder === 'asc' ? 1 : -1;
            }
            if (a[sortField] < b[sortField]) {
                return sortOrder === 'asc' ? -1 : 1;
            }
            return 0;
        });
        setTableData(sortedData);
    }, [sortField, sortOrder]);

    const handleSortClick = (field) => {
        if (sortField === field) {
            setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
        } else {
            setSortField(field);
            setSortOrder('desc');
        }
    };

    return (
        <table>
            <thead>
                <tr>
                    <th onClick={() => handleSortClick('name')}>Name</th>
                    <th onClick={() => handleSortClick('wins')}>Wins</th>
                    <th onClick={() => handleSortClick('losses')}>Losses</th>
                    <th onClick={() => handleSortClick('matches')}>Matches</th>
                    <th onClick={() => handleSortClick('winrate')}>Winrate</th>
                    <th onClick={() => handleSortClick('points')}>Points</th>
                    <th onClick={() => handleSortClick('rank')}>Rank</th>
                </tr>
            </thead>
            <tbody>
                {tableData.map((row, index) => (
                    <tr key={index}>
                        <td>{row.name}</td>
                        <td>{row.wins}</td>
                        <td>{row.losses}</td>
                        <td>{row.matches}</td>
                        <td>{(row.winrate * 100).toFixed(2)}%</td>
                        <td>{row.points}</td>
                        <td>{row.rank}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
}

export default LeagueStatsTable;
